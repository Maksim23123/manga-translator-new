from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt, Signal)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QSizePolicy, QToolButton, QWidget)

from PyFlow.UI.Tool.Tool import ShelfTool
from PyFlow.Core.Common import Direction
from PyFlow.UI.ContextMenuDataBuilder import ContextMenuDataBuilder

try:
    from icons.icons import Icons
except ModuleNotFoundError:
    Icons = None  # type: ignore[assignment]

from qtpy import QtGui


class PreviewShelfTool(ShelfTool, QObject):
    """docstring for DemoShelfTool."""

    triggered = Signal()

    changeImageTriggered = Signal()

    def __init__(self):
        super(PreviewShelfTool, self).__init__()

    def contextMenuBuilder(self):
        builder = ContextMenuDataBuilder()
        builder.addEntry("Change image that will be used for preview", "Change image", self.changeImageTriggered.emit)
        return builder

    @staticmethod
    def toolTip():
        return "Preview pipeline effect of choosen image."

    @staticmethod
    def getIcon():
        if Icons is None:
            return QIcon()
        return QIcon(Icons.PLAY_ICON_PATH)

    @staticmethod
    def name():
        return "Preview"

    def do(self):
        self.triggered.emit()
