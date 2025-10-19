# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'unitListItemFDVNbP.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QWidget)

class Ui_UnitListItem(object):
    def setupUi(self, UnitListItem):
        if not UnitListItem.objectName():
            UnitListItem.setObjectName(u"UnitListItem")
        UnitListItem.resize(464, 44)
        self.horizontalLayout_2 = QHBoxLayout(UnitListItem)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.unitNameLabel = QLabel(UnitListItem)
        self.unitNameLabel.setObjectName(u"unitNameLabel")

        self.horizontalLayout.addWidget(self.unitNameLabel)

        self.isActiveLabel = QLabel(UnitListItem)
        self.isActiveLabel.setObjectName(u"isActiveLabel")

        self.horizontalLayout.addWidget(self.isActiveLabel)

        self.deleteUnitPushButton = QPushButton(UnitListItem)
        self.deleteUnitPushButton.setObjectName(u"deleteUnitPushButton")

        self.horizontalLayout.addWidget(self.deleteUnitPushButton, 0, Qt.AlignmentFlag.AlignRight)


        self.horizontalLayout_2.addLayout(self.horizontalLayout)


        self.retranslateUi(UnitListItem)

        QMetaObject.connectSlotsByName(UnitListItem)
    # setupUi

    def retranslateUi(self, UnitListItem):
        UnitListItem.setWindowTitle(QCoreApplication.translate("UnitListItem", u"Form", None))
        self.unitNameLabel.setText(QCoreApplication.translate("UnitListItem", u"[unit name label]", None))
        self.isActiveLabel.setText("")
        self.deleteUnitPushButton.setText(QCoreApplication.translate("UnitListItem", u"Delete", None))
    # retranslateUi

