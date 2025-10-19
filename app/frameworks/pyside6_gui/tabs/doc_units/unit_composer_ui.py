# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'unit_composervxZUMi.ui'
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
from PySide6.QtWidgets import (QApplication, QDockWidget, QHBoxLayout, QHeaderView,
    QLabel, QListWidget, QListWidgetItem, QMainWindow,
    QPushButton, QScrollArea, QSizePolicy, QTreeView,
    QVBoxLayout, QWidget)

class Ui_UnitComposer(object):
    def setupUi(self, UnitComposer):
        if not UnitComposer.objectName():
            UnitComposer.setObjectName(u"UnitComposer")
        UnitComposer.resize(800, 600)
        self.centralwidget = QWidget(UnitComposer)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.detailsLabel = QLabel(self.centralwidget)
        self.detailsLabel.setObjectName(u"detailsLabel")

        self.verticalLayout_2.addWidget(self.detailsLabel)

        self.details_view_scrollArea = QScrollArea(self.centralwidget)
        self.details_view_scrollArea.setObjectName(u"details_view_scrollArea")
        self.details_view_scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 498, 284))
        self.details_view_scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_2.addWidget(self.details_view_scrollArea)


        self.verticalLayout.addLayout(self.verticalLayout_2)

        UnitComposer.setCentralWidget(self.centralwidget)
        self.unitHierarchyWidget = QDockWidget(UnitComposer)
        self.unitHierarchyWidget.setObjectName(u"unitHierarchyWidget")
        self.dockWidgetContents_15 = QWidget()
        self.dockWidgetContents_15.setObjectName(u"dockWidgetContents_15")
        self.verticalLayout_6 = QVBoxLayout(self.dockWidgetContents_15)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.unitHierarchyTreeView = QTreeView(self.dockWidgetContents_15)
        self.unitHierarchyTreeView.setObjectName(u"unitHierarchyTreeView")

        self.verticalLayout_5.addWidget(self.unitHierarchyTreeView)

        self.importFilesPushButton = QPushButton(self.dockWidgetContents_15)
        self.importFilesPushButton.setObjectName(u"importFilesPushButton")

        self.verticalLayout_5.addWidget(self.importFilesPushButton)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")

        self.verticalLayout_5.addLayout(self.horizontalLayout_2)


        self.verticalLayout_6.addLayout(self.verticalLayout_5)

        self.unitHierarchyWidget.setWidget(self.dockWidgetContents_15)
        UnitComposer.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.unitHierarchyWidget)
        self.unitListWidget_2 = QDockWidget(UnitComposer)
        self.unitListWidget_2.setObjectName(u"unitListWidget_2")
        self.dockWidgetContents_16 = QWidget()
        self.dockWidgetContents_16.setObjectName(u"dockWidgetContents_16")
        self.verticalLayout_4 = QVBoxLayout(self.dockWidgetContents_16)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.newUnitButton = QPushButton(self.dockWidgetContents_16)
        self.newUnitButton.setObjectName(u"newUnitButton")

        self.horizontalLayout.addWidget(self.newUnitButton, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)


        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.unitListWidget = QListWidget(self.dockWidgetContents_16)
        self.unitListWidget.setObjectName(u"unitListWidget")

        self.verticalLayout_3.addWidget(self.unitListWidget)


        self.verticalLayout_4.addLayout(self.verticalLayout_3)

        self.unitListWidget_2.setWidget(self.dockWidgetContents_16)
        UnitComposer.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.unitListWidget_2)

        self.retranslateUi(UnitComposer)

        QMetaObject.connectSlotsByName(UnitComposer)
    # setupUi

    def retranslateUi(self, UnitComposer):
        UnitComposer.setWindowTitle(QCoreApplication.translate("UnitComposer", u"MainWindow", None))
        self.detailsLabel.setText(QCoreApplication.translate("UnitComposer", u"Details", None))
        self.unitHierarchyWidget.setWindowTitle(QCoreApplication.translate("UnitComposer", u"Manga Hierarchy", None))
        self.importFilesPushButton.setText(QCoreApplication.translate("UnitComposer", u"Import files", None))
        self.unitListWidget_2.setWindowTitle(QCoreApplication.translate("UnitComposer", u"Manga list", None))
        self.newUnitButton.setText(QCoreApplication.translate("UnitComposer", u"New Manga", None))
    # retranslateUi

