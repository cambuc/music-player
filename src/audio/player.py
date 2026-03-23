from __future__ import annotations
import random

import vlc
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from data.models import Song, Playlist


class AudioPlayer(QObject):
    progress_updated = pyqtSignal(int, int)   # (position_ms, duration_ms)
    song_changed = pyqtSignal(object)          # Song
    playback_state_changed = pyqtSignal(bool)  # True = playing
    queue_updated = pyqtSignal()               # queue contents changed

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._instance = vlc.Instance("--quiet")
        self._player: vlc.MediaPlayer = self._instance.media_player_new()

        self._playlist: Playlist | None = None
        self._queue: list[Song] = []
        self._current_idx: int = 0
        self._shuffle: bool = False
        self._loop: bool = False

        self._timer = QTimer(self)
        self._timer.setInterval(200)
        self._timer.timeout.connect(self._on_poll)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def play_song(self, song: Song, playlist: Playlist, start_index: int = 0) -> None:
        self._playlist = playlist
        self._build_queue(song, start_index)
        self._load_and_play(song)

    def play_pause(self) -> None:
        state = self._player.get_state()
        if state == vlc.State.Playing:
            self._player.pause()
            self.playback_state_changed.emit(False)
        elif state in (vlc.State.Paused, vlc.State.Stopped, vlc.State.Ended):
            if not self._queue:
                return
            if state == vlc.State.Stopped or state == vlc.State.Ended:
                self._load_and_play(self._queue[self._current_idx])
            else:
                self._player.play()
                self.playback_state_changed.emit(True)

    def next(self) -> None:
        if not self._queue:
            return
        self._current_idx = (self._current_idx + 1) % len(self._queue)
        self._load_and_play(self._queue[self._current_idx])

    def prev(self) -> None:
        if not self._queue:
            return
        pos = self._player.get_time()
        if pos > 3000:
            self._player.set_time(0)
        else:
            self._current_idx = (self._current_idx - 1) % len(self._queue)
            self._load_and_play(self._queue[self._current_idx])

    def seek(self, position_ms: int) -> None:
        self._player.set_time(position_ms)

    def set_volume(self, volume: int) -> None:
        self._player.audio_set_volume(max(0, min(100, volume)))

    def set_shuffle(self, enabled: bool) -> None:
        self._shuffle = enabled
        if self._playlist is None:
            return
        current_song = self._queue[self._current_idx] if self._queue else None
        if enabled:
            indices = list(range(len(self._playlist.songs)))
            random.shuffle(indices)
            self._queue = [self._playlist.songs[i] for i in indices]
            if current_song and current_song in self._queue:
                self._queue.remove(current_song)
                self._queue.insert(0, current_song)
                self._current_idx = 0
        else:
            self._queue = list(self._playlist.songs)
            if current_song and current_song in self._queue:
                self._current_idx = self._queue.index(current_song)

    def set_loop(self, enabled: bool) -> None:
        self._loop = enabled
        self.queue_updated.emit()

    def get_queue(self) -> tuple[Song | None, list[Song]]:
        current = self._queue[self._current_idx] if self._queue else None
        upcoming = self._queue[self._current_idx + 1:] if self._queue else []
        return current, list(upcoming)

    def add_to_queue(self, song: Song) -> None:
        self._queue.append(song)
        self.queue_updated.emit()

    def reorder_queue(self, new_upcoming: list[Song]) -> None:
        self._queue = self._queue[: self._current_idx + 1] + new_upcoming
        self.queue_updated.emit()

    def remove_from_queue(self, upcoming_index: int) -> None:
        target = self._current_idx + 1 + upcoming_index
        if 0 <= target < len(self._queue):
            self._queue.pop(target)
            self.queue_updated.emit()

    def stop(self) -> None:
        self._timer.stop()
        self._player.stop()
        self.playback_state_changed.emit(False)

    def current_song(self) -> Song | None:
        if self._queue and 0 <= self._current_idx < len(self._queue):
            return self._queue[self._current_idx]
        return None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_queue(self, song: Song, start_index: int) -> None:
        if self._playlist is None:
            self._queue = [song]
            self._current_idx = 0
            return

        if self._shuffle:
            indices = list(range(len(self._playlist.songs)))
            random.shuffle(indices)
            self._queue = [self._playlist.songs[i] for i in indices]
            if song in self._queue:
                self._queue.remove(song)
                self._queue.insert(0, song)
            self._current_idx = 0
        else:
            self._queue = list(self._playlist.songs)
            self._current_idx = start_index

    def _load_and_play(self, song: Song) -> None:
        media = self._instance.media_new(song.file_path)
        self._player.set_media(media)
        self._player.play()
        self._timer.start()
        self.song_changed.emit(song)
        self.playback_state_changed.emit(True)
        self.queue_updated.emit()

    def _on_poll(self) -> None:
        state = self._player.get_state()
        if state == vlc.State.Playing:
            pos = self._player.get_time()
            dur = self._player.get_length()
            if pos >= 0 and dur > 0:
                self.progress_updated.emit(pos, dur)
        elif state == vlc.State.Ended:
            if self._current_idx == len(self._queue) - 1 and not self._loop:
                self._timer.stop()
                self.playback_state_changed.emit(False)
            else:
                self.next()
