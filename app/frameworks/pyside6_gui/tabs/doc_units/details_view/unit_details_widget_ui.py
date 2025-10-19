# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'unitDetailsWidgetPpvzJa.ui'
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

class Ui_UnitDetailsWidget(object):
    def setupUi(self, UnitDetailsWidget):
        if not UnitDetailsWidget.objectName():
            UnitDetailsWidget.setObjectName(u"UnitDetailsWidget")
        UnitDetailsWidget.resize(567, 111)
        self.verticalLayout_2 = QVBoxLayout(UnitDetailsWidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.unit_name_label = QLabel(UnitDetailsWidget)
        self.unit_name_label.setObjectName(u"unit_name_label")

        self.horizontalLayout.addWidget(self.unit_name_label, 0, Qt.AlignmentFlag.AlignTop)

        self.unit_name_lineEdit = QLineEdit(UnitDetailsWidget)
        self.unit_name_lineEdit.setObjectName(u"unit_name_lineEdit")

        self.horizontalLayout.addWidget(self.unit_name_lineEdit, 0, Qt.AlignmentFlag.AlignTop)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.unit_path_label = QLabel(UnitDetailsWidget)
        self.unit_path_label.setObjectName(u"unit_path_label")

        self.horizontalLayout_5.addWidget(self.unit_path_label, 0, Qt.AlignmentFlag.AlignTop)

        self.unit_path_lineEdit = QLineEdit(UnitDetailsWidget)
        self.unit_path_lineEdit.setObjectName(u"unit_path_lineEdit")
        self.unit_path_lineEdit.setEnabled(True)
        self.unit_path_lineEdit.setReadOnly(True)

        self.horizontalLayout_5.addWidget(self.unit_path_lineEdit, 0, Qt.AlignmentFlag.AlignTop)


        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.save_changes_pushButton = QPushButton(UnitDetailsWidget)
        self.save_changes_pushButton.setObjectName(u"save_changes_pushButton")

        self.horizontalLayout_6.addWidget(self.save_changes_pushButton)

        self.discard_changes_pushButton = QPushButton(UnitDetailsWidget)
        self.discard_changes_pushButton.setObjectName(u"discard_changes_pushButton")

        self.horizontalLayout_6.addWidget(self.discard_changes_pushButton)


        self.verticalLayout.addLayout(self.horizontalLayout_6)


        self.verticalLayout_2.addLayout(self.verticalLayout)


        self.retranslateUi(UnitDetailsWidget)

        QMetaObject.connectSlotsByName(UnitDetailsWidget)
    # setupUi

    def retranslateUi(self, UnitDetailsWidget):
        UnitDetailsWidget.setWindowTitle(QCoreApplication.translate("UnitDetailsWidget", u"Form", None))
        self.unit_name_label.setText(QCoreApplication.translate("UnitDetailsWidget", u"Manga name", None))
        self.unit_path_label.setText(QCoreApplication.translate("UnitDetailsWidget", u"Manga path", None))
        self.unit_path_lineEdit.setText(QCoreApplication.translate("UnitDetailsWidget", u"[Path]", None))
        self.save_changes_pushButton.setText(QCoreApplication.translate("UnitDetailsWidget", u"Save changes", None))
        self.discard_changes_pushButton.setText(QCoreApplication.translate("UnitDetailsWidget", u"Discard changes", None))
    # retranslateUi

