# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pipelinesListyHFgdJ.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QListWidget, QListWidgetItem,
    QSizePolicy, QSpacerItem, QToolButton, QVBoxLayout,
    QWidget)

class Ui_PipelinesList(object):
    def setupUi(self, PipelinesList):
        if not PipelinesList.objectName():
            PipelinesList.setObjectName(u"PipelinesList")
        PipelinesList.resize(285, 372)
        self.verticalLayout_2 = QVBoxLayout(PipelinesList)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.new_pipeline_toolButton = QToolButton(PipelinesList)
        self.new_pipeline_toolButton.setObjectName(u"new_pipeline_toolButton")
        icon = QIcon(QIcon.fromTheme(u"list-add"))
        self.new_pipeline_toolButton.setIcon(icon)

        self.horizontalLayout.addWidget(self.new_pipeline_toolButton)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.pipelines_list_listWidget = QListWidget(PipelinesList)
        self.pipelines_list_listWidget.setObjectName(u"pipelines_list_listWidget")

        self.verticalLayout.addWidget(self.pipelines_list_listWidget)


        self.verticalLayout_2.addLayout(self.verticalLayout)


        self.retranslateUi(PipelinesList)

        QMetaObject.connectSlotsByName(PipelinesList)
    # setupUi

    def retranslateUi(self, PipelinesList):
        PipelinesList.setWindowTitle(QCoreApplication.translate("PipelinesList", u"Form", None))
        self.new_pipeline_toolButton.setText(QCoreApplication.translate("PipelinesList", u"...", None))
    # retranslateUi

