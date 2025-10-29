# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pipelinePropertiesEkuyxC.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_PipelineProperties(object):
    def setupUi(self, PipelineProperties):
        if not PipelineProperties.objectName():
            PipelineProperties.setObjectName(u"PipelineProperties")
        PipelineProperties.resize(400, 300)
        self.verticalLayout_2 = QVBoxLayout(PipelineProperties)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.pipeline_name_label = QLabel(PipelineProperties)
        self.pipeline_name_label.setObjectName(u"pipeline_name_label")

        self.horizontalLayout_5.addWidget(self.pipeline_name_label)

        self.pipeline_name_lineEdit = QLineEdit(PipelineProperties)
        self.pipeline_name_lineEdit.setObjectName(u"pipeline_name_lineEdit")

        self.horizontalLayout_5.addWidget(self.pipeline_name_lineEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.save_changes_pushButton = QPushButton(PipelineProperties)
        self.save_changes_pushButton.setObjectName(u"save_changes_pushButton")

        self.horizontalLayout.addWidget(self.save_changes_pushButton)

        self.discard_changes_pushButton = QPushButton(PipelineProperties)
        self.discard_changes_pushButton.setObjectName(u"discard_changes_pushButton")

        self.horizontalLayout.addWidget(self.discard_changes_pushButton)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.verticalLayout_2.addLayout(self.verticalLayout)


        self.retranslateUi(PipelineProperties)

        QMetaObject.connectSlotsByName(PipelineProperties)
    # setupUi

    def retranslateUi(self, PipelineProperties):
        PipelineProperties.setWindowTitle(QCoreApplication.translate("PipelineProperties", u"Form", None))
        self.pipeline_name_label.setText(QCoreApplication.translate("PipelineProperties", u"Pipeline name", None))
        self.save_changes_pushButton.setText(QCoreApplication.translate("PipelineProperties", u"Save", None))
        self.discard_changes_pushButton.setText(QCoreApplication.translate("PipelineProperties", u"Discard", None))
    # retranslateUi

