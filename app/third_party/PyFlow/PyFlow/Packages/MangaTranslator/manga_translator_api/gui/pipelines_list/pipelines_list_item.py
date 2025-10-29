from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt, Signal)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QListWidget, QListWidgetItem,
    QSizePolicy, QSpacerItem, QToolButton, QVBoxLayout,
    QWidget)

from .pipelines_list_item_ui import Ui_PipelinesListItem



class PipelinesListItem(QWidget, QObject):

    ACTIVE_ITEM_MARK = "active"


    deletePipelineTriggered = Signal(str)

    
    def __init__(self, item_name: str, is_active: bool=False, parent: QWidget|None=None):
        super().__init__(parent)
        self.is_active = is_active
        self._item_name = item_name
        self.event_connection = None

        self._setup_ui()
        self._wrap_signals()

        self.pipeline_name_label.setText(self._item_name)

        self.set_active(is_active)
    

    def _wrap_signals(self):
        self.delete_pipeline_toolButton.clicked.connect(self._on_delete_pipeline)


    def _setup_ui(self):
        self.ui = Ui_PipelinesListItem()
        self.ui.setupUi(self)

        self.pipeline_name_label = self.ui.pipeline_name_label
        self.pipeline_status_label = self.ui.pipeline_status_label
        self.delete_pipeline_toolButton = self.ui.delete_pipeline_toolButton
    

    @property
    def item_name(self):
        return self._item_name
    

    @item_name.setter
    def item_name(self, value: str):
        self._item_name = value
        self.pipeline_name_label.setText(self._item_name)


    def set_active(self, is_active: bool=False):
        status_label_text = self.ACTIVE_ITEM_MARK if is_active else ""
        self.pipeline_status_label.setText(status_label_text)
    

    def _on_delete_pipeline(self):
        self.deletePipelineTriggered.emit(self._item_name)