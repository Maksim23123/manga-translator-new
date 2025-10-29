from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QHeaderView, QLabel, QSizePolicy, QTreeView,
    QVBoxLayout, QWidget)

from .preview_image_selection_dialog_ui import Ui_PreviewImageSelectionDialog



class PreviewImageSelectionDialog(QDialog):
    def __init__(self, parent: QWidget|None = None):
        super().__init__(parent)

        self._apply_ui()
        self._setup_ui()
    

    def _apply_ui(self):
        self.ui = Ui_PreviewImageSelectionDialog()
        self.ui.setupUi(self)

        self.current_unit_name_Label = self.ui.current_unit_name_Label
        self.unit_content_treeView = self.ui.unit_content_treeView
        self.accept_pushButton = self.ui.accept_pushButton
        self.reject_pushButton = self.ui.reject_pushButton
    

    def _setup_ui(self):
        self.setWindowTitle("Set preview image")