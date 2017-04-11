# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(962, 851)
        MainWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.gb_dsm_search_result = QtWidgets.QGroupBox(self.splitter)
        self.gb_dsm_search_result.setTitle("")
        self.gb_dsm_search_result.setObjectName("gb_dsm_search_result")
        self.gridLayout = QtWidgets.QGridLayout(self.gb_dsm_search_result)
        self.gridLayout.setObjectName("gridLayout")
        self.edt_dsm_search_keyword = QtWidgets.QLineEdit(self.gb_dsm_search_result)
        self.edt_dsm_search_keyword.setObjectName("edt_dsm_search_keyword")
        self.gridLayout.addWidget(self.edt_dsm_search_keyword, 0, 3, 1, 1)
        self.label = QtWidgets.QLabel(self.gb_dsm_search_result)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 2, 1, 1)
        self.btn_dsm_search = QtWidgets.QPushButton(self.gb_dsm_search_result)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_dsm_search.sizePolicy().hasHeightForWidth())
        self.btn_dsm_search.setSizePolicy(sizePolicy)
        self.btn_dsm_search.setStyleSheet("QPushButton\n"
"{\n"
"    background-image:url(:/interface/res/interface/btn_search.png);\n"
"    background-repeat:no-repeat;\n"
"    background-position: center center;\n"
"    border:none;\n"
"}\n"
"QPushButton:hover\n"
"{\n"
"    background-image:url(:/interface/res/interface/btn_search_hover.png);\n"
"}\n"
"QPushButton:checked {\n"
"    background-image:url(:/interface/res/interface/btn_stop.png);\n"
"}\n"
"QPushButton:checked:hover {\n"
"    background-image:url(:/interface/res/interface/btn_stop_hover.png);\n"
"}")
        self.btn_dsm_search.setText("")
        self.btn_dsm_search.setCheckable(True)
        self.btn_dsm_search.setObjectName("btn_dsm_search")
        self.gridLayout.addWidget(self.btn_dsm_search, 0, 4, 1, 1)
        self.cb_dsm_search_kind = QtWidgets.QComboBox(self.gb_dsm_search_result)
        self.cb_dsm_search_kind.setMinimumSize(QtCore.QSize(181, 26))
        self.cb_dsm_search_kind.setMaximumSize(QtCore.QSize(181, 26))
        self.cb_dsm_search_kind.setFrame(True)
        self.cb_dsm_search_kind.setObjectName("cb_dsm_search_kind")
        self.gridLayout.addWidget(self.cb_dsm_search_kind, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.gb_dsm_search_result)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.lst_dsm_search_result = QtWidgets.QListWidget(self.gb_dsm_search_result)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setItalic(True)
        self.lst_dsm_search_result.setFont(font)
        self.lst_dsm_search_result.setIconSize(QtCore.QSize(120, 180))
        self.lst_dsm_search_result.setMovement(QtWidgets.QListView.Static)
        self.lst_dsm_search_result.setFlow(QtWidgets.QListView.LeftToRight)
        self.lst_dsm_search_result.setResizeMode(QtWidgets.QListView.Adjust)
        self.lst_dsm_search_result.setLayoutMode(QtWidgets.QListView.SinglePass)
        self.lst_dsm_search_result.setViewMode(QtWidgets.QListView.IconMode)
        self.lst_dsm_search_result.setWordWrap(False)
        self.lst_dsm_search_result.setObjectName("lst_dsm_search_result")
        self.gridLayout.addWidget(self.lst_dsm_search_result, 1, 0, 1, 5)
        self.groupBox = QtWidgets.QGroupBox(self.splitter)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(12, 5, 12, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.cb_current_video = QtWidgets.QComboBox(self.groupBox)
        self.cb_current_video.setObjectName("cb_current_video")
        self.horizontalLayout_2.addWidget(self.cb_current_video)
        self.btn_meta_search = QtWidgets.QPushButton(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_meta_search.sizePolicy().hasHeightForWidth())
        self.btn_meta_search.setSizePolicy(sizePolicy)
        self.btn_meta_search.setStyleSheet("QPushButton\n"
"{\n"
"    background-image:url(:/interface/res/interface/btn_search.png);\n"
"    background-repeat:no-repeat;\n"
"    background-position: center center;\n"
"    border:none;\n"
"}\n"
"QPushButton:hover\n"
"{\n"
"    background-image:url(:/interface/res/interface/btn_search_hover.png);\n"
"}\n"
"QPushButton:checked {\n"
"    background-image:url(:/interface/res/interface/btn_stop.png);\n"
"}\n"
"QPushButton:checked:hover {\n"
"    background-image:url(:/interface/res/interface/btn_stop_hover.png);\n"
"}")
        self.btn_meta_search.setText("")
        self.btn_meta_search.setCheckable(True)
        self.btn_meta_search.setFlat(False)
        self.btn_meta_search.setObjectName("btn_meta_search")
        self.horizontalLayout_2.addWidget(self.btn_meta_search)
        self.btn_save = QtWidgets.QPushButton(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_save.sizePolicy().hasHeightForWidth())
        self.btn_save.setSizePolicy(sizePolicy)
        self.btn_save.setFlat(False)
        self.btn_save.setObjectName("btn_save")
        self.horizontalLayout_2.addWidget(self.btn_save)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.tabWidget = QtWidgets.QTabWidget(self.groupBox)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_meta = QtWidgets.QWidget()
        self.tab_meta.setObjectName("tab_meta")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.tab_meta)
        self.horizontalLayout.setContentsMargins(12, 12, 12, 12)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.table_video_meta = TblMetadata(self.tab_meta)
        self.table_video_meta.setFrameShadow(QtWidgets.QFrame.Raised)
        self.table_video_meta.setShowGrid(False)
        self.table_video_meta.setObjectName("table_video_meta")
        self.table_video_meta.setColumnCount(0)
        self.table_video_meta.setRowCount(0)
        self.table_video_meta.horizontalHeader().setVisible(False)
        self.table_video_meta.horizontalHeader().setHighlightSections(False)
        self.table_video_meta.verticalHeader().setVisible(False)
        self.table_video_meta.verticalHeader().setHighlightSections(False)
        self.horizontalLayout.addWidget(self.table_video_meta)
        self.tabWidget.addTab(self.tab_meta, "")
        self.tab_pices = QtWidgets.QWidget()
        self.tab_pices.setObjectName("tab_pices")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab_pices)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.lst_pices = QtWidgets.QListWidget(self.tab_pices)
        self.lst_pices.setObjectName("lst_pices")
        self.gridLayout_2.addWidget(self.lst_pices, 0, 0, 1, 4)
        self.btn_add_pic = QtWidgets.QToolButton(self.tab_pices)
        self.btn_add_pic.setObjectName("btn_add_pic")
        self.gridLayout_2.addWidget(self.btn_add_pic, 1, 0, 1, 1)
        self.btn_del_pic = QtWidgets.QToolButton(self.tab_pices)
        self.btn_del_pic.setObjectName("btn_del_pic")
        self.gridLayout_2.addWidget(self.btn_del_pic, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.tab_pices)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setStyleSheet("color:rgb(161, 88, 255)")
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 1, 2, 1, 1)
        self.hs_zoom = QtWidgets.QSlider(self.tab_pices)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.hs_zoom.sizePolicy().hasHeightForWidth())
        self.hs_zoom.setSizePolicy(sizePolicy)
        self.hs_zoom.setOrientation(QtCore.Qt.Horizontal)
        self.hs_zoom.setObjectName("hs_zoom")
        self.gridLayout_2.addWidget(self.hs_zoom, 1, 3, 1, 1)
        self.tabWidget.addTab(self.tab_pices, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.verticalLayout_2.addWidget(self.splitter)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Synology 视频元数据修改工具"))
        self.edt_dsm_search_keyword.setStatusTip(_translate("MainWindow", "输入关键字查找(留空表示显示当前资料库全部视频)"))
        self.edt_dsm_search_keyword.setPlaceholderText(_translate("MainWindow", "输入关键字查找(留空表示显示全部视频)"))
        self.label.setText(_translate("MainWindow", "关键字"))
        self.btn_dsm_search.setStatusTip(_translate("MainWindow", "查找VideoStation视频"))
        self.cb_dsm_search_kind.setStatusTip(_translate("MainWindow", "VideoStation资料库"))
        self.label_2.setText(_translate("MainWindow", "范围"))
        self.lst_dsm_search_result.setToolTip(_translate("MainWindow", "双击选择影片进行下一步操作"))
        self.cb_current_video.setStatusTip(_translate("MainWindow", "当前修改的视频"))
        self.btn_meta_search.setStatusTip(_translate("MainWindow", "查找当前视频元数据"))
        self.btn_save.setStatusTip(_translate("MainWindow", "保存修改结果到VideoStation"))
        self.btn_save.setText(_translate("MainWindow", "保存"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_meta), _translate("MainWindow", "元数据"))
        self.btn_add_pic.setText(_translate("MainWindow", "+"))
        self.btn_del_pic.setText(_translate("MainWindow", "-"))
        self.label_3.setText(_translate("MainWindow", "可以直接拖入多张图片，前两张图片会写入VideoStation。第一张为海报，第二张为背景；在列表内拖动图片可以调整图片顺序。"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_pices), _translate("MainWindow", "海报"))

from widgets.tbl_edit_metadata import TblMetadata
import ui.res_rc_rc
