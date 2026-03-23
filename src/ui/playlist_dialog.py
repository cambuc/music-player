from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QSizePolicy,
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from utils.image_utils import scaled_fill


class PlaylistDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("New Playlist")
        self.setModal(True)
        self.setMinimumWidth(360)
        self._cover_path: str | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        title = QLabel("Create Playlist")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(title)

        # Cover art preview + choose button
        art_row = QHBoxLayout()
        self._cover_preview = QLabel()
        self._cover_preview.setFixedSize(80, 80)
        self._cover_preview.setStyleSheet("background-color: #2A2A2A; border-radius: 4px;")
        self._cover_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._cover_preview.setText("🎵")
        self._cover_preview.setStyleSheet(
            "background-color: #2A2A2A; border-radius: 4px; font-size: 28px;"
        )
        art_row.addWidget(self._cover_preview)

        art_col = QVBoxLayout()
        art_col.setSpacing(6)
        art_label = QLabel("Cover Art")
        art_label.setStyleSheet("color: #B3B3B3; font-size: 12px;")
        art_col.addWidget(art_label)
        choose_btn = QPushButton("Choose Image")
        choose_btn.setObjectName("ChooseImageBtn")
        choose_btn.clicked.connect(self._on_choose_image)
        art_col.addWidget(choose_btn)
        art_col.addStretch()
        art_row.addLayout(art_col)
        art_row.addStretch()
        layout.addLayout(art_row)

        # Name field
        name_label = QLabel("Playlist Name")
        name_label.setStyleSheet("color: #B3B3B3; font-size: 12px;")
        layout.addWidget(name_label)
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("My Playlist")
        layout.addWidget(self._name_edit)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("DialogCancelBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        ok_btn = QPushButton("Create")
        ok_btn.setObjectName("DialogOkBtn")
        ok_btn.clicked.connect(self._on_ok)
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)

    def _on_choose_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Cover Art",
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp)",
        )
        if path:
            self._cover_path = path
            self._cover_preview.setPixmap(scaled_fill(QPixmap(path), 80, 80))
            self._cover_preview.setText("")

    def _on_ok(self) -> None:
        if self._name_edit.text().strip():
            self.accept()

    def get_result(self) -> tuple[str, str | None]:
        return self._name_edit.text().strip(), self._cover_path
