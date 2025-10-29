# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PreviewImageSelectionDialogoNmkrs.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QHeaderView,
    QLabel, QPushButton, QSizePolicy, QTreeView,
    QVBoxLayout, QWidget)

class Ui_PreviewImageSelectionDialog(object):
    def setupUi(self, PreviewImageSelectionDialog):
        if not PreviewImageSelectionDialog.objectName():
            PreviewImageSelectionDialog.setObjectName(u"PreviewImageSelectionDialog")
        PreviewImageSelectionDialog.resize(298, 329)
        self.verticalLayout_2 = QVBoxLayout(PreviewImageSelectionDialog)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.current_unit_name_Label = QLabel(PreviewImageSelectionDialog)
        self.current_unit_name_Label.setObjectName(u"current_unit_name_Label")

        self.verticalLayout.addWidget(self.current_unit_name_Label)

        self.unit_content_treeView = QTreeView(PreviewImageSelectionDialog)
        self.unit_content_treeView.setObjectName(u"unit_content_treeView")

        self.verticalLayout.addWidget(self.unit_content_treeView)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.accept_pushButton = QPushButton(PreviewImageSelectionDialog)
        self.accept_pushButton.setObjectName(u"accept_pushButton")

        self.horizontalLayout.addWidget(self.accept_pushButton)

        self.reject_pushButton = QPushButton(PreviewImageSelectionDialog)
        self.reject_pushButton.setObjectName(u"reject_pushButton")

        self.horizontalLayout.addWidget(self.reject_pushButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.retranslateUi(PreviewImageSelectionDialog)

        QMetaObject.connectSlotsByName(PreviewImageSelectionDialog)
    # setupUi

    def retranslateUi(self, PreviewImageSelectionDialog):
        PreviewImageSelectionDialog.setWindowTitle(QCoreApplication.translate("PreviewImageSelectionDialog", u"Dialog", None))
        self.current_unit_name_Label.setText("")
        self.accept_pushButton.setText(QCoreApplication.translate("PreviewImageSelectionDialog", u"Ok", None))
        self.reject_pushButton.setText(QCoreApplication.translate("PreviewImageSelectionDialog", u"Cancel", None))
    # retranslateUi

