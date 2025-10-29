from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QHBoxLayout, QLabel, QLineEdit, QSizePolicy,
    QVBoxLayout, QWidget)

from .new_pipeline_dialog_ui import Ui_NewPipelineDialog


class NewPipelineDialog(QDialog):

    WINDOW_TITLE = "New pipeline"

    def __init__(self, parent: QWidget|None=None):
        super().__init__(parent)

        self._setup_ui()
        self._setup()
    
    

    def _setup_ui(self):
        self.ui = Ui_NewPipelineDialog()
        self.ui.setupUi(self)

        self.pipeline_name_lineEdit = self.ui.pipeline_name_lineEdit


    def _setup(self):
        self.setWindowTitle(self.WINDOW_TITLE)
    
    @property
    def pipeline_name(self):
        return self.pipeline_name_lineEdit.text()
