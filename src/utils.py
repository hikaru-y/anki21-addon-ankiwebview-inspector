from pathlib import Path

from aqt import qt, theme


# https://lists.qt-project.org/pipermail/qt-interest-old/2008-December/000776.html
def get_icon(path: str) -> qt.QIcon:
    icon = qt.QIcon(str(Path(__file__).resolve().parent / path))
    if theme.theme_manager.night_mode:
        img = icon.pixmap(32).toImage()
        img.invertPixels()
        icon = qt.QIcon(qt.QPixmap.fromImage(img))
    return icon
