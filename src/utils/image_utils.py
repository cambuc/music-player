from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


def scaled_fill(pixmap: QPixmap, width: int, height: int) -> QPixmap:
    """Scale image to fill target dimensions, cropping to center (no letterboxing)."""
    if pixmap.isNull():
        return pixmap
    scaled = pixmap.scaled(
        width, height,
        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        Qt.TransformationMode.SmoothTransformation,
    )
    x = (scaled.width() - width) // 2
    y = (scaled.height() - height) // 2
    return scaled.copy(x, y, width, height)
