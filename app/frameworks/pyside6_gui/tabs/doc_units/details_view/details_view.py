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
from .unit_details_widget import UnitDetailsWidget
from .hierarchy_item_details_widget import HierarchyItemDetailsWidget


class DetailsView(QWidget):

    NONE_SELECTED_DISPLAY_MODE = 0
    UNIT_DISPLAY_MODE = 1
    HIERARCHY_ITEM_DISPLAY_MODE = 2

    def __init__(self):
        super().__init__()

        self.main_layout = QVBoxLayout(self)

        self._init_widgets()

        self.switch_display_mode(self.NONE_SELECTED_DISPLAY_MODE)
    

    def _init_widgets(self):
        self._set_up_none_selected_widget()

        self.unit_details_widget = UnitDetailsWidget()
        self.main_layout.addWidget(self.unit_details_widget)

        self.hierarchy_item_details_widget = HierarchyItemDetailsWidget()
        self.main_layout.addWidget(self.hierarchy_item_details_widget)


    def _set_up_none_selected_widget(self):
        NONE_SELECTED_LABEL_TEXT = "Nothing was selected"
        self.none_selected_widget = QWidget(self)
        
        none_selected_widget_layout = QVBoxLayout(self.none_selected_widget)
        none_selected_label = QLabel(NONE_SELECTED_LABEL_TEXT)

        none_selected_widget_layout.addWidget(none_selected_label, 0, (Qt.AlignmentFlag.AlignVCenter 
                                                                       | Qt.AlignmentFlag.AlignHCenter))

        self.main_layout.addWidget(self.none_selected_widget)
    

    def _hide_all(self):
        self.unit_details_widget.hide()
        self.none_selected_widget.hide()
        self.hierarchy_item_details_widget.hide()


    def switch_display_mode(self, display_mode) -> bool:
        if display_mode == self.NONE_SELECTED_DISPLAY_MODE:
            self._hide_all()
            self.none_selected_widget.show()
            return True
        elif display_mode == self.UNIT_DISPLAY_MODE:
            self._hide_all()
            self.unit_details_widget.show()
            return True
        elif display_mode == self.HIERARCHY_ITEM_DISPLAY_MODE:
            self._hide_all()
            self.hierarchy_item_details_widget.show()
            return True
        else:
            return False
