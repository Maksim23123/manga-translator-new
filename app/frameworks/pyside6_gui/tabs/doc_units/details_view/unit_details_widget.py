from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDockWidget, QHBoxLayout, QHeaderView,
    QLabel, QListWidget, QListWidgetItem, QMainWindow,
    QPushButton, QScrollArea, QSizePolicy, QTreeView,
    QVBoxLayout, QWidget)
from .unit_details_widget_ui import Ui_UnitDetailsWidget


class UnitDetailsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()
    

    def _setup_ui(self):
        self.ui = Ui_UnitDetailsWidget()
        self.ui.setupUi(self)

        self.unit_name_lineEdit = self.ui.unit_name_lineEdit
        self.unit_path_lineEdit = self.ui.unit_path_lineEdit
        self.save_changes_pushButton = self.ui.save_changes_pushButton
        self.discard_changes_pushButton = self.ui.discard_changes_pushButton
        