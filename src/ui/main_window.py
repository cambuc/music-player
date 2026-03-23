from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter
from PyQt6.QtCore import Qt

from data.store import DataStore
from data.models import Playlist, Song
from audio.player import AudioPlayer
from ui.sidebar import Sidebar
from ui.song_list import SongListPanel
from ui.player_bar import PlayerBar
from ui.queue_panel import QueuePanel


class MainWindow(QMainWindow):
    def __init__(self, store: DataStore, player: AudioPlayer) -> None:
        super().__init__()
        self._store = store
        self._player = player
        self._current_playlist: Playlist | None = None

        self.setWindowTitle("Music Player")
        self.setMinimumSize(900, 600)
        self.resize(1100, 700)

        self._build_ui()
        self._connect_signals()

        # Load initial data
        self._sidebar.refresh(self._store.get_playlists())

        # Apply initial volume
        self._player.set_volume(self._player_bar.get_volume())

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Main content: sidebar | song list | queue panel (hidden)
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._sidebar = Sidebar()
        self._song_list = SongListPanel(self._store)
        self._queue_panel = QueuePanel()
        self._queue_panel.setVisible(False)
        self._splitter.addWidget(self._sidebar)
        self._splitter.addWidget(self._song_list)
        self._splitter.addWidget(self._queue_panel)
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)
        self._splitter.setStretchFactor(2, 0)
        self._splitter.setSizes([240, 860, 0])
        root.addWidget(self._splitter, stretch=1)

        # Player bar pinned at bottom
        self._player_bar = PlayerBar()
        root.addWidget(self._player_bar)

    def _connect_signals(self) -> None:
        # Sidebar → store / UI
        self._sidebar.playlist_created.connect(self._on_playlist_created)
        self._sidebar.playlist_selected.connect(self._on_playlist_selected)
        self._sidebar.playlist_deleted.connect(self._on_playlist_deleted)

        # Song list → player / sidebar
        self._song_list.song_double_clicked.connect(self._on_song_double_clicked)
        self._song_list.play_playlist.connect(self._on_play_playlist)
        self._song_list.songs_changed.connect(self._on_songs_changed)
        self._song_list.shuffle_play_playlist.connect(self._on_shuffle_play_playlist)
        self._song_list.add_to_queue_requested.connect(self._player.add_to_queue)

        # Player bar controls → audio player
        self._player_bar.play_pause_clicked.connect(self._player.play_pause)
        self._player_bar.next_clicked.connect(self._player.next)
        self._player_bar.prev_clicked.connect(self._player.prev)
        self._player_bar.seek_requested.connect(self._player.seek)
        self._player_bar.volume_changed.connect(self._player.set_volume)
        self._player_bar.shuffle_toggled.connect(self._player.set_shuffle)
        self._player_bar.queue_toggled.connect(self._on_queue_toggled)
        self._player_bar.loop_toggled.connect(self._player.set_loop)

        # Audio player → player bar / song list / queue
        self._player.progress_updated.connect(self._player_bar.update_seek_slider)
        self._player.song_changed.connect(self._on_song_changed)
        self._player.playback_state_changed.connect(self._player_bar.update_play_button)
        self._player.queue_updated.connect(self._on_queue_updated)

        # Queue panel
        self._queue_panel.close_requested.connect(self._on_queue_close)
        self._queue_panel.queue_reordered.connect(self._player.reorder_queue)
        self._queue_panel.remove_from_queue_requested.connect(self._player.remove_from_queue)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_playlist_created(self, playlist: Playlist) -> None:
        self._store.add_playlist(playlist)
        self._sidebar.refresh(self._store.get_playlists())

    def _on_playlist_selected(self, playlist: Playlist) -> None:
        fresh = next((p for p in self._store.get_playlists() if p.id == playlist.id), playlist)
        self._current_playlist = fresh
        self._song_list.load_playlist(fresh)

    def _on_playlist_deleted(self, playlist_id: str) -> None:
        playlist = next((p for p in self._store.get_playlists() if p.id == playlist_id), None)
        song_paths = [s.file_path for s in playlist.songs] if playlist else []
        self._store.delete_playlist(playlist_id)
        for path in song_paths:
            if not self._store.is_file_referenced(path):
                try:
                    Path(path).unlink(missing_ok=True)
                except Exception:
                    pass
        if self._current_playlist and self._current_playlist.id == playlist_id:
            self._current_playlist = None
            self._song_list.clear()
        self._sidebar.refresh(self._store.get_playlists())

    def _on_song_double_clicked(self, song: Song, playlist: Playlist) -> None:
        idx = next((i for i, s in enumerate(playlist.songs) if s.id == song.id), 0)
        self._player.play_song(song, playlist, start_index=idx)

    def _on_play_playlist(self, playlist: Playlist) -> None:
        if playlist.songs:
            self._player.play_song(playlist.songs[0], playlist, start_index=0)

    def _on_shuffle_play_playlist(self, playlist: Playlist) -> None:
        if playlist.songs:
            self._player.set_shuffle(True)
            self._player_bar.set_shuffle(True)
            self._player.play_song(playlist.songs[0], playlist, start_index=0)

    def _on_songs_changed(self) -> None:
        self._sidebar.refresh(self._store.get_playlists())

    def _on_song_changed(self, song: Song) -> None:
        cover = None
        if self._current_playlist:
            cover = self._current_playlist.cover_art_path
        self._player_bar.update_song_info(song, cover)
        self._song_list.highlight_song(song)

    def _on_queue_toggled(self, visible: bool) -> None:
        self._queue_panel.setVisible(visible)
        if visible:
            self._splitter.setSizes([240, 600, 260])
            self._on_queue_updated()
        else:
            self._splitter.setSizes([240, 860, 0])

    def _on_queue_close(self) -> None:
        self._queue_panel.setVisible(False)
        self._player_bar.set_queue_visible(False)
        self._splitter.setSizes([240, 860, 0])

    def _on_queue_updated(self) -> None:
        if self._queue_panel.isVisible():
            current, upcoming = self._player.get_queue()
            self._queue_panel.refresh(current, upcoming)
