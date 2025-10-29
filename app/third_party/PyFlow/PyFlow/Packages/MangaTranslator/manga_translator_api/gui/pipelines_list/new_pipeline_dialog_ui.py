# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'NewPipelineDialogGtiaZb.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QHBoxLayout, QLabel, QLineEdit, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_NewPipelineDialog(object):
    def setupUi(self, NewPipelineDialog):
        if not NewPipelineDialog.objectName():
            NewPipelineDialog.setObjectName(u"NewPipelineDialog")
        NewPipelineDialog.resize(233, 71)
        self.verticalLayout = QVBoxLayout(NewPipelineDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pipeline_name_label = QLabel(NewPipelineDialog)
        self.pipeline_name_label.setObjectName(u"pipeline_name_label")

        self.horizontalLayout.addWidget(self.pipeline_name_label)

        self.pipeline_name_lineEdit = QLineEdit(NewPipelineDialog)
        self.pipeline_name_lineEdit.setObjectName(u"pipeline_name_lineEdit")

        self.horizontalLayout.addWidget(self.pipeline_name_lineEdit)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.dialog_buttonBox = QDialogButtonBox(NewPipelineDialog)
        self.dialog_buttonBox.setObjectName(u"dialog_buttonBox")
        self.dialog_buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.dialog_buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.dialog_buttonBox)


        self.retranslateUi(NewPipelineDialog)
        self.dialog_buttonBox.accepted.connect(NewPipelineDialog.accept)
        self.dialog_buttonBox.rejected.connect(NewPipelineDialog.reject)

        QMetaObject.connectSlotsByName(NewPipelineDialog)
    # setupUi

    def retranslateUi(self, NewPipelineDialog):
        NewPipelineDialog.setWindowTitle(QCoreApplication.translate("NewPipelineDialog", u"Dialog", None))
        self.pipeline_name_label.setText(QCoreApplication.translate("NewPipelineDialog", u"Pipeline name", None))
    # retranslateUi

