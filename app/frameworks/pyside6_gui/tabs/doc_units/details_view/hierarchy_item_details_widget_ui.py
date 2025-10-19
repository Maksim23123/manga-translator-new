# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'hierarchyItemDetailsWidgetvJbZAZ.ui'
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
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_HierarchyItemDetailsWidget(object):
    def setupUi(self, HierarchyItemDetailsWidget):
        if not HierarchyItemDetailsWidget.objectName():
            HierarchyItemDetailsWidget.setObjectName(u"HierarchyItemDetailsWidget")
        HierarchyItemDetailsWidget.resize(422, 390)
        self.verticalLayout_2 = QVBoxLayout(HierarchyItemDetailsWidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.image_preview_label = QLabel(HierarchyItemDetailsWidget)
        self.image_preview_label.setObjectName(u"image_preview_label")

        self.verticalLayout.addWidget(self.image_preview_label, 0, Qt.AlignmentFlag.AlignHCenter)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.item_name_label = QLabel(HierarchyItemDetailsWidget)
        self.item_name_label.setObjectName(u"item_name_label")

        self.horizontalLayout.addWidget(self.item_name_label)

        self.item_name_lineEdit = QLineEdit(HierarchyItemDetailsWidget)
        self.item_name_lineEdit.setObjectName(u"item_name_lineEdit")
        self.item_name_lineEdit.setEnabled(True)
        self.item_name_lineEdit.setReadOnly(True)

        self.horizontalLayout.addWidget(self.item_name_lineEdit)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.item_type_label = QLabel(HierarchyItemDetailsWidget)
        self.item_type_label.setObjectName(u"item_type_label")

        self.horizontalLayout_2.addWidget(self.item_type_label)

        self.item_type_lineEdit = QLineEdit(HierarchyItemDetailsWidget)
        self.item_type_lineEdit.setObjectName(u"item_type_lineEdit")
        self.item_type_lineEdit.setEnabled(True)
        self.item_type_lineEdit.setReadOnly(True)

        self.horizontalLayout_2.addWidget(self.item_type_lineEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.children_number_widget = QWidget(HierarchyItemDetailsWidget)
        self.children_number_widget.setObjectName(u"children_number_widget")
        self.horizontalLayout_4 = QHBoxLayout(self.children_number_widget)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.children_number_label = QLabel(self.children_number_widget)
        self.children_number_label.setObjectName(u"children_number_label")

        self.horizontalLayout_3.addWidget(self.children_number_label)

        self.children_number_lineEdit = QLineEdit(self.children_number_widget)
        self.children_number_lineEdit.setObjectName(u"children_number_lineEdit")
        self.children_number_lineEdit.setEnabled(True)
        self.children_number_lineEdit.setReadOnly(True)

        self.horizontalLayout_3.addWidget(self.children_number_lineEdit)


        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)


        self.verticalLayout.addWidget(self.children_number_widget)

        self.image_path_widget = QWidget(HierarchyItemDetailsWidget)
        self.image_path_widget.setObjectName(u"image_path_widget")
        self.horizontalLayout_6 = QHBoxLayout(self.image_path_widget)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.image_path_label = QLabel(self.image_path_widget)
        self.image_path_label.setObjectName(u"image_path_label")

        self.horizontalLayout_5.addWidget(self.image_path_label)

        self.image_path_lineEdit = QLineEdit(self.image_path_widget)
        self.image_path_lineEdit.setObjectName(u"image_path_lineEdit")
        self.image_path_lineEdit.setEnabled(True)
        self.image_path_lineEdit.setReadOnly(True)

        self.horizontalLayout_5.addWidget(self.image_path_lineEdit)


        self.horizontalLayout_6.addLayout(self.horizontalLayout_5)


        self.verticalLayout.addWidget(self.image_path_widget)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.verticalLayout_2.addLayout(self.verticalLayout)


        self.retranslateUi(HierarchyItemDetailsWidget)

        QMetaObject.connectSlotsByName(HierarchyItemDetailsWidget)
    # setupUi

    def retranslateUi(self, HierarchyItemDetailsWidget):
        HierarchyItemDetailsWidget.setWindowTitle(QCoreApplication.translate("HierarchyItemDetailsWidget", u"Form", None))
        self.image_preview_label.setText("")
        self.item_name_label.setText(QCoreApplication.translate("HierarchyItemDetailsWidget", u"Name", None))
        self.item_type_label.setText(QCoreApplication.translate("HierarchyItemDetailsWidget", u"Type", None))
        self.children_number_label.setText(QCoreApplication.translate("HierarchyItemDetailsWidget", u"Number of children", None))
        self.image_path_label.setText(QCoreApplication.translate("HierarchyItemDetailsWidget", u"Image path", None))
    # retranslateUi

