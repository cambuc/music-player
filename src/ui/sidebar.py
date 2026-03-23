from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QSizePolicy, QFrame, QMenu,
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal

from data.models import Playlist
from utils.image_utils import scaled_fill
from ui.playlist_dialog import PlaylistDialog


class PlaylistItem(QWidget):
    clicked = pyqtSignal(object)   # Playlist
    delete_requested = pyqtSignal(str)  # playlist id

    def __init__(self, playlist: Playlist, parent=None) -> None:
        super().__init__(parent)
        self.playlist = playlist
        self._selected = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)

        # Thumbnail
        self._thumb = QLabel()
        self._thumb.setFixedSize(44, 44)
        self._thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._thumb.setStyleSheet(
            "background-color: #2A2A2A; border-radius: 4px; font-size: 18px;"
        )
        self._update_thumb()
        layout.addWidget(self._thumb)

        # Text
        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        self._name_label = QLabel(self.playlist.name)
        self._name_label.setStyleSheet("color: #FFFFFF; font-size: 13px; font-weight: 500;")
        self._name_label.setWordWrap(False)
        count = len(self.playlist.songs)
        self._count_label = QLabel(f"{count} song{'s' if count != 1 else ''}")
        self._count_label.setStyleSheet("color: #B3B3B3; font-size: 11px;")
        text_col.addWidget(self._name_label)
        text_col.addWidget(self._count_label)
        layout.addLayout(text_col)
        layout.addStretch()

    def _update_thumb(self) -> None:
        if self.playlist.cover_art_path:
            try:
                self._thumb.setPixmap(scaled_fill(QPixmap(self.playlist.cover_art_path), 44, 44))
                self._thumb.setText("")
                return
            except Exception:
                pass
        self._thumb.setText("🎵")

    def set_selected(self, selected: bool) -> None:
        self._selected = selected
        if selected:
            self.setStyleSheet("background-color: #333333; border-radius: 4px;")
        else:
            self.setStyleSheet("background-color: transparent; border-radius: 4px;")

    def refresh(self) -> None:
        self._name_label.setText(self.playlist.name)
        count = len(self.playlist.songs)
        self._count_label.setText(f"{count} song{'s' if count != 1 else ''}")
        self._update_thumb()

    def enterEvent(self, event) -> None:
        if not self._selected:
            self.setStyleSheet("background-color: #1A1A1A; border-radius: 4px;")
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        if not self._selected:
            self.setStyleSheet("background-color: transparent; border-radius: 4px;")
        super().leaveEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.playlist)
        super().mousePressEvent(event)

    def _on_context_menu(self, pos) -> None:
        menu = QMenu(self)
        delete_action = menu.addAction("Delete Playlist")
        action = menu.exec(self.mapToGlobal(pos))
        if action == delete_action:
            self.delete_requested.emit(self.playlist.id)


class Sidebar(QWidget):
    playlist_selected = pyqtSignal(object)   # Playlist
    playlist_created = pyqtSignal(object)    # Playlist
    playlist_deleted = pyqtSignal(str)       # playlist id

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setMinimumWidth(220)
        self.setMaximumWidth(280)
        self._items: list[PlaylistItem] = []
        self._selected_id: str | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 16, 8, 8)
        layout.setSpacing(8)

        header = QLabel("MY PLAYLISTS")
        header.setStyleSheet("color: #B3B3B3; font-size: 11px; font-weight: bold; letter-spacing: 1px; padding-left: 8px;")
        layout.addWidget(header)

        # Scroll area for playlist items
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._container = QWidget()
        self._container.setStyleSheet("background-color: transparent;")
        self._list_layout = QVBoxLayout(self._container)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(2)
        self._list_layout.addStretch()
        self._scroll.setWidget(self._container)
        layout.addWidget(self._scroll)

        # New playlist button
        new_btn = QPushButton("＋  New Playlist")
        new_btn.setObjectName("NewPlaylistBtn")
        new_btn.setToolTip("New playlist")
        new_btn.clicked.connect(self._on_new_playlist)
        layout.addWidget(new_btn)

    def refresh(self, playlists: list[Playlist]) -> None:
        # Remove old items (all except the stretch at the end)
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._items.clear()

        for playlist in playlists:
            item = PlaylistItem(playlist)
            item.clicked.connect(self._on_item_clicked)
            item.delete_requested.connect(self.playlist_deleted)
            if playlist.id == self._selected_id:
                item.set_selected(True)
            self._list_layout.insertWidget(self._list_layout.count() - 1, item)
            self._items.append(item)

    def _on_item_clicked(self, playlist: Playlist) -> None:
        self._selected_id = playlist.id
        for item in self._items:
            item.set_selected(item.playlist.id == playlist.id)
        self.playlist_selected.emit(playlist)

    def _on_new_playlist(self) -> None:
        dialog = PlaylistDialog(self)
        if dialog.exec() == PlaylistDialog.DialogCode.Accepted:
            name, cover_path = dialog.get_result()
            if name:
                playlist = Playlist(name=name, cover_art_path=cover_path)
                self.playlist_created.emit(playlist)
