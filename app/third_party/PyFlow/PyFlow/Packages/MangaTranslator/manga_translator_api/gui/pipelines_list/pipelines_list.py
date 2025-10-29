from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QListWidget, QListWidgetItem,
    QSizePolicy, QSpacerItem, QToolButton, QVBoxLayout,
    QWidget)

from .pipelines_list_ui import Ui_PipelinesList


class PipelinesList(QWidget):

    def __init__(self, parent: QWidget|None=None):
        super().__init__(parent)

        self._setup_ui()


    def _setup_ui(self):
        self.ui = Ui_PipelinesList()
        self.ui.setupUi(self)

        self.pipelines_list_listWidget = self.ui.pipelines_list_listWidget
        self.new_pipeline_toolButton = self.ui.new_pipeline_toolButton