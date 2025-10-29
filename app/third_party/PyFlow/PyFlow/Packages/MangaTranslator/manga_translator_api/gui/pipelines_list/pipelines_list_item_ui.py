# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pipelinesListItemMeXngU.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QSizePolicy, QToolButton, QWidget)

class Ui_PipelinesListItem(object):
    def setupUi(self, PipelinesListItem):
        if not PipelinesListItem.objectName():
            PipelinesListItem.setObjectName(u"PipelinesListItem")
        PipelinesListItem.resize(307, 42)
        self.horizontalLayout_2 = QHBoxLayout(PipelinesListItem)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pipeline_name_label = QLabel(PipelinesListItem)
        self.pipeline_name_label.setObjectName(u"pipeline_name_label")

        self.horizontalLayout.addWidget(self.pipeline_name_label)

        self.line = QFrame(PipelinesListItem)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout.addWidget(self.line)

        self.pipeline_status_label = QLabel(PipelinesListItem)
        self.pipeline_status_label.setObjectName(u"pipeline_status_label")

        self.horizontalLayout.addWidget(self.pipeline_status_label)

        self.delete_pipeline_toolButton = QToolButton(PipelinesListItem)
        self.delete_pipeline_toolButton.setObjectName(u"delete_pipeline_toolButton")
        icon = QIcon(QIcon.fromTheme(u"edit-delete"))
        self.delete_pipeline_toolButton.setIcon(icon)

        self.horizontalLayout.addWidget(self.delete_pipeline_toolButton)


        self.horizontalLayout_2.addLayout(self.horizontalLayout)


        self.retranslateUi(PipelinesListItem)

        QMetaObject.connectSlotsByName(PipelinesListItem)
    # setupUi

    def retranslateUi(self, PipelinesListItem):
        PipelinesListItem.setWindowTitle(QCoreApplication.translate("PipelinesListItem", u"Form", None))
        self.pipeline_name_label.setText("")
        self.pipeline_status_label.setText("")
        self.delete_pipeline_toolButton.setText(QCoreApplication.translate("PipelinesListItem", u"...", None))
    # retranslateUi

