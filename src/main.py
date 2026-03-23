import os
import sys
from pathlib import Path

# ── VLC path setup (Windows) ─────────────────────────────────────────
_vlc_candidates = [
    r"C:\Program Files\VideoLAN\VLC",
    r"C:\Program Files (x86)\VideoLAN\VLC",
]
for _vlc_path in _vlc_candidates:
    _dll = os.path.join(_vlc_path, "libvlc.dll")
    if os.path.exists(_dll):
        if hasattr(os, "add_dll_directory"):
            os.add_dll_directory(_vlc_path)
        os.environ["PATH"] = _vlc_path + os.pathsep + os.environ.get("PATH", "")
        os.environ.setdefault("VLC_PLUGIN_PATH", os.path.join(_vlc_path, "plugins"))
        break

# ── Ensure src/ is on the import path ────────────────────────────────
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from PyQt6.QtWidgets import QApplication, QMessageBox

try:
    import vlc as _vlc_test
    _inst = _vlc_test.Instance("--quiet")
    if _inst is None:
        raise RuntimeError("vlc.Instance() returned None")
except Exception as _e:
    _searched = "\n".join(f"  • {p}" for p in _vlc_candidates)
    app = QApplication(sys.argv)
    QMessageBox.critical(
        None,
        "VLC Not Found",
        f"Could not initialise VLC.\n\nError: {_e}\n\n"
        f"Searched for libvlc.dll in:\n{_searched}\n\n"
        "Make sure VLC media player is installed and try again.",
    )
    sys.exit(1)

from PyQt6.QtGui import QIcon
from data.store import DataStore
from audio.player import AudioPlayer
from ui.main_window import MainWindow
from ui.theme import apply_theme

_ICON_PATH = SRC_DIR.parent / "assets" / "icons" / "app_icon.svg"


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Music Player")
    if _ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(_ICON_PATH)))

    apply_theme(app)

    store = DataStore()
    player = AudioPlayer()
    window = MainWindow(store, player)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
