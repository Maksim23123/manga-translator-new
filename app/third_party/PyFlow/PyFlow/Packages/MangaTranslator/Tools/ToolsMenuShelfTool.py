from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt, Signal)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)

from PyFlow.UI.Tool.Tool import ShelfTool
from PyFlow.Core.Common import Direction

try:
    from icons.icons import Icons
except ModuleNotFoundError:
    Icons = None  # type: ignore[assignment]

from qtpy import QtGui


class ToolsMenuShelfTool(ShelfTool, QObject):
    """docstring for DemoShelfTool."""

    triggered = Signal()

    def __init__(self):
        super(ToolsMenuShelfTool, self).__init__()

    @staticmethod
    def toolTip():
        return "Show menu of available tools."

    @staticmethod
    def getIcon():
        if Icons is None:
            return QIcon()
        return QIcon(Icons.SETTINGS_ICON_PATH)

    @staticmethod
    def name():
        return "Tools menu"

    def do(self):
        self.triggered.emit()
