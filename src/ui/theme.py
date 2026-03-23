from PyQt6.QtWidgets import QApplication

QSS = """
/* ── Tooltip ──────────────────────────────────────────────────── */
QToolTip {
    background-color: #282828;
    color: #FFFFFF;
    border: 1px solid #535353;
    padding: 4px 8px;
    font-size: 11px;
    border-radius: 3px;
}

/* ── Base ─────────────────────────────────────────────────────── */
QMainWindow, QWidget {
    background-color: #121212;
    color: #FFFFFF;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 14px;
}

QDialog {
    background-color: #181818;
    color: #FFFFFF;
}

QLabel {
    background-color: transparent;
    color: #FFFFFF;
}

/* ── Sidebar ──────────────────────────────────────────────────── */
#Sidebar {
    background-color: #000000;
    border-right: 1px solid #282828;
}

/* ── SongListPanel ────────────────────────────────────────────── */
#SongListPanel {
    background-color: #121212;
}

/* ── PlayerBar ────────────────────────────────────────────────── */
#PlayerBar {
    background-color: #181818;
    border-top: 1px solid #282828;
}

/* ── Table ────────────────────────────────────────────────────── */
QTableWidget {
    background-color: #121212;
    gridline-color: transparent;
    selection-background-color: #333333;
    selection-color: #FFFFFF;
    border: none;
    outline: 0;
}
QTableWidget::item {
    padding: 4px 8px;
    border: none;
}
QTableWidget::item:hover {
    background-color: #2A2A2A;
}
QHeaderView::section {
    background-color: #121212;
    color: #B3B3B3;
    font-size: 11px;
    border: none;
    padding: 6px 8px;
    border-bottom: 1px solid #282828;
}
QHeaderView {
    background-color: #121212;
}

/* ── Sliders ──────────────────────────────────────────────────── */
QSlider::groove:horizontal {
    height: 4px;
    background: #535353;
    border-radius: 2px;
}
QSlider::sub-page:horizontal {
    background: #1DB954;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #FFFFFF;
    width: 12px;
    height: 12px;
    margin: -4px 0;
    border-radius: 6px;
}
QSlider::handle:horizontal:hover {
    background: #1ED760;
}

/* ── Playback Buttons ─────────────────────────────────────────── */
QPushButton#PlayPauseBtn {
    background-color: #FFFFFF;
    border-radius: 16px;
    min-width: 32px;
    max-width: 32px;
    min-height: 32px;
    max-height: 32px;
    color: #000000;
    font-size: 16px;
    font-weight: bold;
    border: none;
}
QPushButton#PlayPauseBtn:hover {
    background-color: #E0E0E0;
}

QPushButton#PrevBtn,
QPushButton#NextBtn,
QPushButton#ShuffleBtn {
    background: transparent;
    border: none;
    color: #B3B3B3;
    font-size: 18px;
    min-width: 32px;
    min-height: 32px;
}
QPushButton#PrevBtn:hover,
QPushButton#NextBtn:hover {
    color: #FFFFFF;
}
QPushButton#ShuffleBtn:checked {
    color: #1DB954;
}
QPushButton#ShuffleBtn:hover {
    color: #FFFFFF;
}

/* ── Sidebar Buttons ──────────────────────────────────────────── */
QPushButton#NewPlaylistBtn {
    background-color: transparent;
    border: 1px solid #535353;
    border-radius: 4px;
    color: #B3B3B3;
    padding: 6px;
    text-align: left;
}
QPushButton#NewPlaylistBtn:hover {
    border-color: #FFFFFF;
    color: #FFFFFF;
}

/* ── Song List Action Buttons ─────────────────────────────────── */
QPushButton#AddSongsBtn,
QPushButton#PlayAllBtn {
    background-color: transparent;
    border: 1px solid #535353;
    border-radius: 20px;
    color: #B3B3B3;
    padding: 6px 16px;
    font-size: 13px;
}
QPushButton#AddSongsBtn:hover,
QPushButton#PlayAllBtn:hover {
    border-color: #FFFFFF;
    color: #FFFFFF;
}
QPushButton#AddSongsBtn:disabled {
    border-color: #333333;
    color: #535353;
}
/* ── Shuffle Play Button ──────────────────────────────────────── */
QPushButton#ShufflePlayBtn {
    background-color: transparent;
    border: 1px solid #535353;
    border-radius: 20px;
    color: #B3B3B3;
    padding: 6px 16px;
    font-size: 13px;
}
QPushButton#ShufflePlayBtn:hover {
    border-color: #FFFFFF;
    color: #FFFFFF;
}

/* ── Playlist Dialog Buttons ──────────────────────────────────── */
QPushButton#ChooseImageBtn {
    background-color: #2A2A2A;
    border: 1px solid #535353;
    border-radius: 4px;
    color: #B3B3B3;
    padding: 8px;
}
QPushButton#ChooseImageBtn:hover {
    border-color: #FFFFFF;
    color: #FFFFFF;
}

QPushButton#DialogOkBtn {
    background-color: #1DB954;
    border: none;
    border-radius: 20px;
    color: #000000;
    padding: 8px 24px;
    font-weight: bold;
}
QPushButton#DialogOkBtn:hover {
    background-color: #1ED760;
}

QPushButton#DialogCancelBtn {
    background-color: transparent;
    border: 1px solid #535353;
    border-radius: 20px;
    color: #B3B3B3;
    padding: 8px 24px;
}
QPushButton#DialogCancelBtn:hover {
    border-color: #FFFFFF;
    color: #FFFFFF;
}

/* ── Line Edit ────────────────────────────────────────────────── */
QLineEdit {
    background-color: #2A2A2A;
    border: 1px solid #535353;
    border-radius: 4px;
    color: #FFFFFF;
    padding: 8px;
}
QLineEdit:focus {
    border-color: #1DB954;
}

/* ── Scroll Bar ───────────────────────────────────────────────── */
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #535353;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background: #B3B3B3;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: transparent;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

/* ── Splitter ─────────────────────────────────────────────────── */
QSplitter::handle {
    background-color: #282828;
    width: 1px;
}

/* ── Queue Button (player bar) ────────────────────────────────── */
QPushButton#QueueBtn {
    background: transparent;
    border: none;
    color: #B3B3B3;
    font-size: 16px;
    min-width: 32px;
    min-height: 32px;
}
QPushButton#QueueBtn:hover {
    color: #FFFFFF;
}
QPushButton#QueueBtn:checked {
    color: #1DB954;
}

/* ── Loop Button (player bar) ─────────────────────────────────── */
QPushButton#LoopBtn {
    background: transparent;
    border: none;
    color: #B3B3B3;
    font-size: 16px;
    min-width: 32px;
    min-height: 32px;
}
QPushButton#LoopBtn:hover {
    color: #FFFFFF;
}
QPushButton#LoopBtn:checked {
    color: #1DB954;
}

/* ── Queue Close Button ───────────────────────────────────────── */
QPushButton#QueueCloseBtn {
    background: transparent;
    border: none;
    color: #B3B3B3;
    font-size: 14px;
    min-width: 28px;
    max-width: 28px;
    min-height: 28px;
    max-height: 28px;
}
QPushButton#QueueCloseBtn:hover {
    color: #FFFFFF;
}

/* ── Queue Panel ──────────────────────────────────────────────── */
#QueuePanel {
    background-color: #0A0A0A;
    border-left: 1px solid #282828;
}

QListWidget#QueueList {
    background-color: #0A0A0A;
    border: none;
    outline: 0;
}
QListWidget#QueueList::item {
    padding: 8px 12px;
    border-radius: 4px;
    color: #B3B3B3;
    font-size: 13px;
}
QListWidget#QueueList::item:hover {
    background-color: #2A2A2A;
    color: #FFFFFF;
}
QListWidget#QueueList::item:selected {
    background-color: #333333;
    color: #FFFFFF;
}

/* ── Context Menu ─────────────────────────────────────────────── */
QMenu {
    background-color: #282828;
    border: 1px solid #404040;
    border-radius: 4px;
    padding: 4px;
    color: #FFFFFF;
    font-size: 13px;
}
QMenu::item {
    padding: 8px 24px 8px 12px;
    border-radius: 3px;
}
QMenu::item:selected {
    background-color: #3A3A3A;
}
QMenu::item:disabled {
    color: #535353;
}
QMenu::separator {
    height: 1px;
    background: #404040;
    margin: 4px 8px;
}
"""


def apply_theme(app: QApplication) -> None:
    app.setStyleSheet(QSS)
