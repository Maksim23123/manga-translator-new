from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)
from .pipeline_properties_ui import Ui_PipelineProperties



class PipelineProperties(QWidget):
    def __init__(self, parent: QWidget|None = None):
        super().__init__(parent)
        self._setup_ui()


    def _setup_ui(self):
        self.ui = Ui_PipelineProperties()
        self.ui.setupUi(self)

        self.pipeline_name_lineEdit = self.ui.pipeline_name_lineEdit
        self.save_changes_pushButton = self.ui.save_changes_pushButton
        self.discard_changes_pushButton = self.ui.discard_changes_pushButton