from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QSlider, QSizePolicy,
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal

from data.models import Song
from utils.image_utils import scaled_fill


class PlayerBar(QWidget):
    play_pause_clicked = pyqtSignal()
    next_clicked = pyqtSignal()
    prev_clicked = pyqtSignal()
    seek_requested = pyqtSignal(int)    # position in ms
    volume_changed = pyqtSignal(int)    # 0–100
    shuffle_toggled = pyqtSignal(bool)
    queue_toggled = pyqtSignal(bool)
    loop_toggled = pyqtSignal(bool)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("PlayerBar")
        self.setFixedHeight(90)
        self._is_playing = False
        self._duration_ms = 0
        self._build_ui()

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(16, 0, 16, 0)
        root.setSpacing(0)

        # ── Left: cover + song info ──────────────────────────────────
        left = QHBoxLayout()
        left.setSpacing(12)

        self._cover = QLabel()
        self._cover.setFixedSize(54, 54)
        self._cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._cover.setStyleSheet(
            "background-color: #2A2A2A; border-radius: 4px; font-size: 22px;"
        )
        self._cover.setText("🎵")
        left.addWidget(self._cover)

        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        self._title_label = QLabel("—")
        self._title_label.setStyleSheet("color: #FFFFFF; font-size: 13px; font-weight: 500;")
        self._title_label.setMaximumWidth(200)
        self._artist_label = QLabel("—")
        self._artist_label.setStyleSheet("color: #B3B3B3; font-size: 12px;")
        self._artist_label.setMaximumWidth(200)
        info_col.addWidget(self._title_label)
        info_col.addWidget(self._artist_label)
        left.addLayout(info_col)

        left_widget = QWidget()
        left_widget.setLayout(left)
        left_widget.setMinimumWidth(200)
        root.addWidget(left_widget)

        # ── Center: controls + seek ──────────────────────────────────
        center_col = QVBoxLayout()
        center_col.setSpacing(6)
        center_col.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        btn_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self._prev_btn = QPushButton("⏮")
        self._prev_btn.setObjectName("PrevBtn")
        self._prev_btn.setToolTip("Previous")
        self._prev_btn.clicked.connect(self.prev_clicked)
        btn_row.addWidget(self._prev_btn)

        self._play_btn = QPushButton("▶")
        self._play_btn.setObjectName("PlayPauseBtn")
        self._play_btn.setToolTip("Play / Pause")
        self._play_btn.clicked.connect(self.play_pause_clicked)
        btn_row.addWidget(self._play_btn)

        self._next_btn = QPushButton("⏭")
        self._next_btn.setObjectName("NextBtn")
        self._next_btn.setToolTip("Next")
        self._next_btn.clicked.connect(self.next_clicked)
        btn_row.addWidget(self._next_btn)

        center_col.addLayout(btn_row)

        seek_row = QHBoxLayout()
        seek_row.setSpacing(8)
        self._time_label = QLabel("0:00")
        self._time_label.setStyleSheet("color: #B3B3B3; font-size: 11px; min-width: 32px;")
        self._time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        seek_row.addWidget(self._time_label)

        self._seek_slider = QSlider(Qt.Orientation.Horizontal)
        self._seek_slider.setMinimum(0)
        self._seek_slider.setMaximum(1000)
        self._seek_slider.setValue(0)
        self._seek_slider.setMinimumWidth(240)
        self._seek_slider.sliderReleased.connect(self._on_seek_released)
        seek_row.addWidget(self._seek_slider)

        self._dur_label = QLabel("0:00")
        self._dur_label.setStyleSheet("color: #B3B3B3; font-size: 11px; min-width: 32px;")
        seek_row.addWidget(self._dur_label)
        center_col.addLayout(seek_row)

        center_widget = QWidget()
        center_widget.setLayout(center_col)
        root.addWidget(center_widget, stretch=1)

        # ── Right: shuffle + volume ──────────────────────────────────
        right = QHBoxLayout()
        right.setSpacing(8)
        right.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self._shuffle_btn = QPushButton("⇄")
        self._shuffle_btn.setObjectName("ShuffleBtn")
        self._shuffle_btn.setToolTip("Shuffle")
        self._shuffle_btn.setCheckable(True)
        self._shuffle_btn.toggled.connect(self.shuffle_toggled)
        right.addWidget(self._shuffle_btn)

        self._queue_btn = QPushButton("≡")
        self._queue_btn.setObjectName("QueueBtn")
        self._queue_btn.setCheckable(True)
        self._queue_btn.setToolTip("Queue")
        self._queue_btn.toggled.connect(self.queue_toggled)
        right.addWidget(self._queue_btn)

        self._loop_btn = QPushButton("🔁")
        self._loop_btn.setObjectName("LoopBtn")
        self._loop_btn.setCheckable(True)
        self._loop_btn.setToolTip("Loop")
        self._loop_btn.toggled.connect(self.loop_toggled)
        right.addWidget(self._loop_btn)

        vol_icon = QLabel("🔊")
        vol_icon.setStyleSheet("color: #B3B3B3; font-size: 14px;")
        right.addWidget(vol_icon)

        self._vol_slider = QSlider(Qt.Orientation.Horizontal)
        self._vol_slider.setMinimum(0)
        self._vol_slider.setMaximum(100)
        self._vol_slider.setValue(70)
        self._vol_slider.setFixedWidth(90)
        self._vol_slider.valueChanged.connect(self.volume_changed)
        right.addWidget(self._vol_slider)

        right_widget = QWidget()
        right_widget.setLayout(right)
        right_widget.setMinimumWidth(200)
        root.addWidget(right_widget)

    # ------------------------------------------------------------------
    # Public update methods
    # ------------------------------------------------------------------

    def set_shuffle(self, enabled: bool) -> None:
        self._shuffle_btn.blockSignals(True)
        self._shuffle_btn.setChecked(enabled)
        self._shuffle_btn.blockSignals(False)

    def set_queue_visible(self, visible: bool) -> None:
        self._queue_btn.blockSignals(True)
        self._queue_btn.setChecked(visible)
        self._queue_btn.blockSignals(False)

    def set_loop(self, enabled: bool) -> None:
        self._loop_btn.blockSignals(True)
        self._loop_btn.setChecked(enabled)
        self._loop_btn.blockSignals(False)

    def update_song_info(self, song: Song, cover_art_path: str | None = None) -> None:
        self._title_label.setText(song.title)
        self._artist_label.setText(song.artist)
        self._duration_ms = song.duration_ms
        self._dur_label.setText(song.duration_str())

        if cover_art_path:
            try:
                self._cover.setPixmap(scaled_fill(QPixmap(cover_art_path), 54, 54))
                self._cover.setText("")
                return
            except Exception:
                pass
        self._cover.setPixmap(QPixmap())
        self._cover.setText("🎵")

    def update_play_button(self, is_playing: bool) -> None:
        self._is_playing = is_playing
        self._play_btn.setText("⏸" if is_playing else "▶")

    def update_seek_slider(self, position_ms: int, duration_ms: int) -> None:
        if duration_ms <= 0:
            return
        self._seek_slider.blockSignals(True)
        self._seek_slider.setValue(int(position_ms * 1000 / duration_ms))
        self._seek_slider.blockSignals(False)
        self._time_label.setText(self._ms_to_str(position_ms))
        self._dur_label.setText(self._ms_to_str(duration_ms))

    def get_volume(self) -> int:
        return self._vol_slider.value()

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _on_seek_released(self) -> None:
        if self._duration_ms <= 0:
            return
        ratio = self._seek_slider.value() / 1000.0
        target_ms = int(ratio * self._duration_ms)
        self.seek_requested.emit(target_ms)

    @staticmethod
    def _ms_to_str(ms: int) -> str:
        total = ms // 1000
        m = total // 60
        s = total % 60
        return f"{m}:{s:02d}"
