from __future__ import annotations

import shutil
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QHeaderView, QAbstractItemView, QApplication, QMenu,
)
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtCore import Qt, pyqtSignal, QEvent, QObject

from data.models import Playlist, Song
from data.store import DataStore
from utils.metadata import MetadataReader
from utils.image_utils import scaled_fill

MUSIC_DIR = Path(__file__).resolve().parent.parent.parent / "music"


class ClickableLabel(QLabel):
    """A QLabel that emits clicked() on left mouse press."""
    clicked = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class SongListPanel(QWidget):
    song_double_clicked = pyqtSignal(object, object)  # (Song, Playlist)
    play_playlist = pyqtSignal(object)                 # Playlist
    shuffle_play_playlist = pyqtSignal(object)         # Playlist
    songs_changed = pyqtSignal()                       # emitted after add/cover change
    add_to_queue_requested = pyqtSignal(object)        # Song

    def __init__(self, store: DataStore, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("SongListPanel")
        self._store = store
        self._playlist: Playlist | None = None
        self._hovered_row: int = -1
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Header area ──────────────────────────────────────────────
        self._header = QWidget()
        self._header.setStyleSheet("background-color: #181818;")
        self._header.setFixedHeight(200)
        header_layout = QHBoxLayout(self._header)
        header_layout.setContentsMargins(32, 24, 32, 24)
        header_layout.setSpacing(24)

        self._cover_label = ClickableLabel()
        self._cover_label.setFixedSize(120, 120)
        self._cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._cover_label.setStyleSheet(
            "background-color: #2A2A2A; border-radius: 8px; font-size: 48px;"
        )
        self._cover_label.setText("🎵")
        self._cover_label.setToolTip("Click to change cover art")
        self._cover_label.clicked.connect(self._on_change_cover)
        header_layout.addWidget(self._cover_label)

        info_col = QVBoxLayout()
        info_col.setSpacing(6)
        playlist_type = QLabel("PLAYLIST")
        playlist_type.setStyleSheet("color: #B3B3B3; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        info_col.addWidget(playlist_type)

        self._playlist_name = QLabel("Select a playlist")
        self._playlist_name.setStyleSheet("color: #FFFFFF; font-size: 28px; font-weight: bold;")
        info_col.addWidget(self._playlist_name)

        self._meta_label = QLabel("")
        self._meta_label.setStyleSheet("color: #B3B3B3; font-size: 13px;")
        info_col.addWidget(self._meta_label)

        info_col.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self._play_all_btn = QPushButton("▶  Play")
        self._play_all_btn.setObjectName("PlayAllBtn")
        self._play_all_btn.setToolTip("Play all songs")
        self._play_all_btn.clicked.connect(self._on_play_all)
        self._play_all_btn.setVisible(False)
        btn_row.addWidget(self._play_all_btn)

        self._shuffle_play_btn = QPushButton("🔀  Shuffle")
        self._shuffle_play_btn.setObjectName("ShufflePlayBtn")
        self._shuffle_play_btn.setToolTip("Shuffle play")
        self._shuffle_play_btn.clicked.connect(self._on_shuffle_play)
        self._shuffle_play_btn.setVisible(False)
        btn_row.addWidget(self._shuffle_play_btn)

        self._add_songs_btn = QPushButton("＋  Add Songs")
        self._add_songs_btn.setObjectName("AddSongsBtn")
        self._add_songs_btn.setToolTip("Add songs to this playlist")
        self._add_songs_btn.clicked.connect(self._on_add_songs)
        self._add_songs_btn.setVisible(False)
        btn_row.addWidget(self._add_songs_btn)
        btn_row.addStretch()
        info_col.addLayout(btn_row)

        header_layout.addLayout(info_col)
        header_layout.addStretch()
        layout.addWidget(self._header)

        # ── Song table ───────────────────────────────────────────────
        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["#", "Title", "Date Added", "Duration"])
        header = self._table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(0, 40)
        self._table.setColumnWidth(2, 110)
        self._table.setColumnWidth(3, 70)
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setShowGrid(False)
        self._table.setAlternatingRowColors(False)
        self._table.setSortingEnabled(False)
        self._table.setMouseTracking(True)
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.cellEntered.connect(self._on_cell_entered)
        self._table.cellClicked.connect(self._on_cell_clicked)
        self._table.cellDoubleClicked.connect(self._on_double_click)
        self._table.customContextMenuRequested.connect(self._on_song_context_menu)
        self._table.viewport().installEventFilter(self)
        layout.addWidget(self._table)

        # ── Empty state ──────────────────────────────────────────────
        self._empty_label = QLabel("Select a playlist from the sidebar")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet("color: #808080; font-size: 16px;")
        layout.addWidget(self._empty_label)
        self._table.setVisible(False)

    # ------------------------------------------------------------------
    # Event filter — clears hover when mouse leaves the table
    # ------------------------------------------------------------------

    def eventFilter(self, obj: QObject, event) -> bool:
        if obj is self._table.viewport() and event.type() == QEvent.Type.Leave:
            self._clear_hover()
        return super().eventFilter(obj, event)

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def load_playlist(self, playlist: Playlist) -> None:
        self._playlist = playlist
        self._playlist_name.setText(playlist.name)
        count = len(playlist.songs)
        self._meta_label.setText(
            f"{count} song{'s' if count != 1 else ''}  ·  {playlist.total_duration_str()}"
            if count else "No songs yet"
        )
        self._set_cover(playlist.cover_art_path)
        self._play_all_btn.setVisible(count > 0)
        self._shuffle_play_btn.setVisible(count > 0)
        self._add_songs_btn.setVisible(True)
        self._empty_label.setVisible(False)
        self._table.setVisible(True)
        self._hovered_row = -1
        self._populate_table(playlist.songs)

    def clear(self) -> None:
        self._playlist = None
        self._playlist_name.setText("Select a playlist")
        self._meta_label.setText("")
        self._play_all_btn.setVisible(False)
        self._shuffle_play_btn.setVisible(False)
        self._add_songs_btn.setVisible(False)
        self._table.setRowCount(0)
        self._table.setVisible(False)
        self._empty_label.setVisible(True)
        self._cover_label.setPixmap(QPixmap())
        self._cover_label.setText("🎵")

    def highlight_song(self, song: Song) -> None:
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 0)
            if item:
                s = item.data(Qt.ItemDataRole.UserRole)
                is_active = s and s.id == song.id
                title_item = self._table.item(row, 1)
                if title_item:
                    title_item.setForeground(
                        Qt.GlobalColor.green if is_active else Qt.GlobalColor.white
                    )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _set_cover(self, path: str | None) -> None:
        if path:
            try:
                self._cover_label.setPixmap(scaled_fill(QPixmap(path), 120, 120))
                self._cover_label.setText("")
                return
            except Exception:
                pass
        self._cover_label.setPixmap(QPixmap())
        self._cover_label.setText("🎵")

    def _populate_table(self, songs: list[Song]) -> None:
        self._table.setSortingEnabled(False)
        self._table.setRowCount(0)
        for row, song in enumerate(songs):
            self._table.insertRow(row)
            self._table.setRowHeight(row, 44)

            num_item = QTableWidgetItem(str(row + 1))
            num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            num_item.setForeground(QColor("#B3B3B3"))
            num_item.setData(Qt.ItemDataRole.UserRole, song)
            self._table.setItem(row, 0, num_item)

            title_item = QTableWidgetItem(song.title)
            self._table.setItem(row, 1, title_item)

            date_item = QTableWidgetItem(song.date_added)
            date_item.setForeground(QColor("#B3B3B3"))
            self._table.setItem(row, 2, date_item)

            dur_item = QTableWidgetItem(song.duration_str())
            dur_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            dur_item.setForeground(QColor("#B3B3B3"))
            self._table.setItem(row, 3, dur_item)

    def _copy_to_local(self, src_path: str) -> str:
        MUSIC_DIR.mkdir(parents=True, exist_ok=True)
        src = Path(src_path)
        dest = MUSIC_DIR / src.name
        # If it's already in the music dir, use it as-is
        if dest.resolve() == src.resolve():
            return str(dest)
        # Resolve name conflict
        if dest.exists():
            stem, suffix = src.stem, src.suffix
            i = 1
            while dest.exists():
                dest = MUSIC_DIR / f"{stem}_{i}{suffix}"
                i += 1
        shutil.copy2(src_path, dest)
        return str(dest)

    def _clear_hover(self) -> None:
        if self._hovered_row >= 0:
            item = self._table.item(self._hovered_row, 0)
            if item:
                item.setText(str(self._hovered_row + 1))
                item.setForeground(QColor("#B3B3B3"))
            self._hovered_row = -1

    def _play_row(self, row: int) -> None:
        if self._playlist is None:
            return
        item = self._table.item(row, 0)
        if item is None:
            return
        song = item.data(Qt.ItemDataRole.UserRole)
        if song:
            self.song_double_clicked.emit(song, self._playlist)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_cell_entered(self, row: int, _col: int) -> None:
        if self._hovered_row == row:
            return
        self._clear_hover()
        self._hovered_row = row
        item = self._table.item(row, 0)
        if item:
            item.setText("▶")
            item.setForeground(Qt.GlobalColor.white)

    def _on_cell_clicked(self, row: int, col: int) -> None:
        if col == 0 and self._hovered_row == row:
            self._play_row(row)

    def _on_double_click(self, row: int, _col: int) -> None:
        self._play_row(row)

    def _on_play_all(self) -> None:
        if self._playlist and self._playlist.songs:
            self.play_playlist.emit(self._playlist)

    def _on_shuffle_play(self) -> None:
        if self._playlist and self._playlist.songs:
            self.shuffle_play_playlist.emit(self._playlist)

    def _on_add_songs(self) -> None:
        if self._playlist is None:
            return
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Add Songs", "", "Audio Files (*.mp3 *.wav)",
        )
        if not paths:
            return
        self._add_songs_btn.setEnabled(False)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            for path in paths:
                local_path = self._copy_to_local(path)
                song = MetadataReader.read(local_path)
                self._playlist.songs.append(song)
        finally:
            QApplication.restoreOverrideCursor()
            self._add_songs_btn.setEnabled(True)
        self._store.update_playlist(self._playlist)
        self.load_playlist(self._playlist)
        self.songs_changed.emit()

    def _on_change_cover(self) -> None:
        if self._playlist is None:
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose Cover Art", "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp)",
        )
        if not path:
            return
        self._playlist.cover_art_path = path
        self._store.update_playlist(self._playlist)
        self._set_cover(path)
        self.songs_changed.emit()

    def _on_song_context_menu(self, pos) -> None:
        if self._playlist is None:
            return
        row = self._table.rowAt(pos.y())
        if row < 0:
            return
        item = self._table.item(row, 0)
        if item is None:
            return
        song: Song | None = item.data(Qt.ItemDataRole.UserRole)
        if song is None:
            return

        menu = QMenu(self)
        play_action = menu.addAction("▶  Play")
        queue_action = menu.addAction("＋  Add to Queue")
        menu.addSeparator()
        remove_action = menu.addAction("Remove from Playlist")

        action = menu.exec(self._table.viewport().mapToGlobal(pos))
        if action == play_action:
            self._play_row(row)
        elif action == queue_action:
            self.add_to_queue_requested.emit(song)
        elif action == remove_action:
            self._remove_song(song)

    def _remove_song(self, song: Song) -> None:
        if self._playlist is None:
            return
        self._playlist.songs = [s for s in self._playlist.songs if s.id != song.id]
        self._store.update_playlist(self._playlist)
        if not self._store.is_file_referenced(song.file_path):
            try:
                Path(song.file_path).unlink(missing_ok=True)
            except Exception:
                pass
        self.load_playlist(self._playlist)
        self.songs_changed.emit()
