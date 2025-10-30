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



class InformationShelfTool(ShelfTool, QObject):
    """docstring for DemoShelfTool."""

    triggered = Signal()

    def __init__(self):
        super(InformationShelfTool, self).__init__()

    @staticmethod
    def toolTip():
        return "Information."

    @staticmethod
    def getIcon():
        if Icons is None:
            return QIcon()
        return QIcon(Icons.INFORMATION_ICON_PATH)

    @staticmethod
    def name():
        return "Information"

    def do(self):
        self.triggered.emit()
