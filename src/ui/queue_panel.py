from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QMenu,
)
from PyQt6.QtCore import Qt, pyqtSignal

from data.models import Song


class QueuePanel(QWidget):
    close_requested = pyqtSignal()
    queue_reordered = pyqtSignal(list)       # list[Song] — new upcoming order
    remove_from_queue_requested = pyqtSignal(int)  # upcoming index

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("QueuePanel")
        self.setFixedWidth(260)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Header ───────────────────────────────────────────────────
        header = QWidget()
        header.setStyleSheet("background-color: #0A0A0A;")
        header.setFixedHeight(48)
        header_row = QHBoxLayout(header)
        header_row.setContentsMargins(16, 0, 8, 0)
        title = QLabel("Queue")
        title.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: bold;")
        header_row.addWidget(title)
        header_row.addStretch()
        close_btn = QPushButton("✕")
        close_btn.setObjectName("QueueCloseBtn")
        close_btn.setFixedSize(28, 28)
        close_btn.clicked.connect(self.close_requested)
        header_row.addWidget(close_btn)
        layout.addWidget(header)

        # ── Now Playing ──────────────────────────────────────────────
        self._now_section = QWidget()
        self._now_section.setStyleSheet("background-color: #0A0A0A;")
        now_col = QVBoxLayout(self._now_section)
        now_col.setContentsMargins(16, 12, 16, 8)
        now_col.setSpacing(6)
        now_hdr = QLabel("NOW PLAYING")
        now_hdr.setStyleSheet("color: #B3B3B3; font-size: 10px; font-weight: bold; letter-spacing: 1px;")
        now_col.addWidget(now_hdr)
        self._now_playing_label = QLabel("—")
        self._now_playing_label.setStyleSheet("color: #1DB954; font-size: 13px; font-weight: 500;")
        self._now_playing_label.setWordWrap(True)
        now_col.addWidget(self._now_playing_label)
        layout.addWidget(self._now_section)

        # ── Next Up ───────────────────────────────────────────────────
        next_hdr_widget = QWidget()
        next_hdr_widget.setStyleSheet("background-color: #0A0A0A;")
        next_hdr_layout = QHBoxLayout(next_hdr_widget)
        next_hdr_layout.setContentsMargins(16, 8, 16, 4)
        next_lbl = QLabel("NEXT UP")
        next_lbl.setStyleSheet("color: #B3B3B3; font-size: 10px; font-weight: bold; letter-spacing: 1px;")
        next_hdr_layout.addWidget(next_lbl)
        layout.addWidget(next_hdr_widget)

        self._queue_list = QListWidget()
        self._queue_list.setObjectName("QueueList")
        self._queue_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self._queue_list.setDragEnabled(True)
        self._queue_list.setAcceptDrops(True)
        self._queue_list.setDropIndicatorShown(True)
        self._queue_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self._queue_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._queue_list.model().rowsMoved.connect(self._on_rows_moved)
        self._queue_list.customContextMenuRequested.connect(self._on_queue_context_menu)
        layout.addWidget(self._queue_list)

        self._empty_label = QLabel("No songs in queue")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet("color: #808080; font-size: 13px;")
        self._empty_label.setVisible(False)
        layout.addWidget(self._empty_label)

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def refresh(self, current: Song | None, upcoming: list[Song]) -> None:
        self._now_playing_label.setText(current.title if current else "—")

        self._queue_list.blockSignals(True)
        self._queue_list.clear()
        for song in upcoming:
            item = QListWidgetItem(f"  {song.title}")
            item.setData(Qt.ItemDataRole.UserRole, song)
            item.setToolTip(f"{song.title} — {song.duration_str()}")
            self._queue_list.addItem(item)
        self._queue_list.blockSignals(False)

        has_items = len(upcoming) > 0
        self._queue_list.setVisible(has_items)
        self._empty_label.setVisible(not has_items)

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _on_queue_context_menu(self, pos) -> None:
        row = self._queue_list.indexAt(pos).row()
        if row < 0:
            return
        menu = QMenu(self)
        remove_action = menu.addAction("Remove from Queue")
        action = menu.exec(self._queue_list.viewport().mapToGlobal(pos))
        if action == remove_action:
            self.remove_from_queue_requested.emit(row)

    def _on_rows_moved(self) -> None:
        new_upcoming: list[Song] = []
        for i in range(self._queue_list.count()):
            item = self._queue_list.item(i)
            if item:
                song = item.data(Qt.ItemDataRole.UserRole)
                if song:
                    new_upcoming.append(song)
        self.queue_reordered.emit(new_upcoming)
