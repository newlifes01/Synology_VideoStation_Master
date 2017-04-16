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
        self.label_2 = QtWidgets.QLabel(self.gb_dsm_search_result)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.cb_dsm_search_kind = QtWidgets.QComboBox(self.gb_dsm_search_result)
        self.cb_dsm_search_kind.setMinimumSize(QtCore.QSize(181, 26))
        self.cb_dsm_search_kind.setMaximumSize(QtCore.QSize(181, 26))
        self.cb_dsm_search_kind.setFrame(True)
        self.cb_dsm_search_kind.setObjectName("cb_dsm_search_kind")
        self.gridLayout.addWidget(self.cb_dsm_search_kind, 0, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.gb_dsm_search_result)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 2, 1, 1)
        self.edt_dsm_search_keyword = QtWidgets.QLineEdit(self.gb_dsm_search_result)
        self.edt_dsm_search_keyword.setClearButtonEnabled(True)
        self.edt_dsm_search_keyword.setObjectName("edt_dsm_search_keyword")
        self.gridLayout.addWidget(self.edt_dsm_search_keyword, 0, 3, 1, 1)
        self.chk_only_nil = QtWidgets.QCheckBox(self.gb_dsm_search_result)
        self.chk_only_nil.setObjectName("chk_only_nil")
        self.gridLayout.addWidget(self.chk_only_nil, 0, 4, 1, 1)
        self.btn_dsm_search = QtWidgets.QPushButton(self.gb_dsm_search_result)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_dsm_search.sizePolicy().hasHeightForWidth())
        self.btn_dsm_search.setSizePolicy(sizePolicy)
        self.btn_dsm_search.setStyleSheet("QPushButton\n"
"{\n"
"    background-image:url(:/icons/ui_icons/search.png);\n"
"    background-repeat:no-repeat;\n"
"    background-position: center center;\n"
"    border:none;\n"
"}\n"
"QPushButton:hover\n"
"{\n"
"    background-image:url(:/icons/ui_icons/search (1).png);\n"
"}\n"
"QPushButton:checked {\n"
"    background-image:url(:/icons/ui_icons/stop.png);\n"
"}\n"
"QPushButton:checked:hover {\n"
"    background-image:url(:/icons/ui_icons/stop (1).png);\n"
"}")
        self.btn_dsm_search.setText("")
        self.btn_dsm_search.setCheckable(True)
        self.btn_dsm_search.setObjectName("btn_dsm_search")
        self.gridLayout.addWidget(self.btn_dsm_search, 0, 5, 1, 1)
        self.btn_setting = QtWidgets.QPushButton(self.gb_dsm_search_result)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_setting.sizePolicy().hasHeightForWidth())
        self.btn_setting.setSizePolicy(sizePolicy)
        self.btn_setting.setStyleSheet("QPushButton\n"
"{\n"
"    background-image:url(:/icons/ui_icons/settings.png);\n"
"    background-repeat:no-repeat;\n"
"    background-position: center center;\n"
"    border:none;\n"
"}\n"
"QPushButton:hover\n"
"{\n"
"    background-image:url(:/icons/ui_icons/settings (1).png);\n"
"}")
        self.btn_setting.setText("")
        self.btn_setting.setFlat(False)
        self.btn_setting.setObjectName("btn_setting")
        self.gridLayout.addWidget(self.btn_setting, 0, 6, 1, 1)
        self.tbl_search_result_widget = TblSeacheResult(self.gb_dsm_search_result)
        self.tbl_search_result_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tbl_search_result_widget.setShowGrid(False)
        self.tbl_search_result_widget.setGridStyle(QtCore.Qt.NoPen)
        self.tbl_search_result_widget.setRowCount(0)
        self.tbl_search_result_widget.setColumnCount(4)
        self.tbl_search_result_widget.setObjectName("tbl_search_result_widget")
        self.tbl_search_result_widget.horizontalHeader().setVisible(False)
        self.tbl_search_result_widget.horizontalHeader().setHighlightSections(False)
        self.tbl_search_result_widget.verticalHeader().setVisible(False)
        self.tbl_search_result_widget.verticalHeader().setHighlightSections(False)
        self.gridLayout.addWidget(self.tbl_search_result_widget, 1, 0, 1, 7)
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
"    background-image:url(:/icons/ui_icons/search.png);\n"
"    background-repeat:no-repeat;\n"
"    background-position: center center;\n"
"    border:none;\n"
"}\n"
"QPushButton:hover\n"
"{\n"
"    background-image:url(:/icons/ui_icons/search (1).png);\n"
"}\n"
"QPushButton:checked {\n"
"    background-image:url(:/icons/ui_icons/stop.png);\n"
"}\n"
"QPushButton:checked:hover {\n"
"    background-image:url(:/icons/ui_icons/stop (1).png);\n"
"}")
        self.btn_meta_search.setText("")
        self.btn_meta_search.setCheckable(True)
        self.btn_meta_search.setFlat(False)
        self.btn_meta_search.setObjectName("btn_meta_search")
        self.horizontalLayout_2.addWidget(self.btn_meta_search)
        self.btn_fresh = QtWidgets.QPushButton(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_fresh.sizePolicy().hasHeightForWidth())
        self.btn_fresh.setSizePolicy(sizePolicy)
        self.btn_fresh.setStyleSheet("QPushButton\n"
"{\n"
"    background-image:url(:/icons/ui_icons/refresh-button.png);\n"
"    background-repeat:no-repeat;\n"
"    background-position: center center;\n"
"    border:none;\n"
"}\n"
"QPushButton:hover\n"
"{\n"
"    background-image:url(:/icons/ui_icons/refresh-button (1).png);\n"
"}")
        self.btn_fresh.setText("")
        self.btn_fresh.setFlat(False)
        self.btn_fresh.setObjectName("btn_fresh")
        self.horizontalLayout_2.addWidget(self.btn_fresh)
        self.btn_save = QtWidgets.QPushButton(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_save.sizePolicy().hasHeightForWidth())
        self.btn_save.setSizePolicy(sizePolicy)
        self.btn_save.setStyleSheet("QPushButton\n"
"{\n"
"    background-image:url(:/icons/ui_icons/save.png);\n"
"    background-repeat:no-repeat;\n"
"    background-position: center center;\n"
"    border:none;\n"
"}\n"
"QPushButton:hover\n"
"{\n"
"    background-image:url(:/icons/ui_icons/save (1).png);\n"
"}")
        self.btn_save.setText("")
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
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tab_pices)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.lst_pices = QtWidgets.QListWidget(self.tab_pices)
        self.lst_pices.setObjectName("lst_pices")
        self.verticalLayout_3.addWidget(self.lst_pices)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.btn_add_pic = QtWidgets.QPushButton(self.tab_pices)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_add_pic.sizePolicy().hasHeightForWidth())
        self.btn_add_pic.setSizePolicy(sizePolicy)
        self.btn_add_pic.setStyleSheet("QPushButton\n"
"{\n"
"    background-image:url(:/icons/ui_icons/add.png);\n"
"    background-repeat:no-repeat;\n"
"    background-position: center center;\n"
"    border:none;\n"
"}\n"
"QPushButton:hover\n"
"{\n"
"    background-image:url(:/icons/ui_icons/add (1).png);\n"
"}")
        self.btn_add_pic.setText("")
        self.btn_add_pic.setFlat(False)
        self.btn_add_pic.setObjectName("btn_add_pic")
        self.horizontalLayout_3.addWidget(self.btn_add_pic)
        self.btn_del_pic = QtWidgets.QPushButton(self.tab_pices)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_del_pic.sizePolicy().hasHeightForWidth())
        self.btn_del_pic.setSizePolicy(sizePolicy)
        self.btn_del_pic.setStyleSheet("QPushButton\n"
"{\n"
"    background-image:url(:/icons/ui_icons/substract.png);\n"
"    background-repeat:no-repeat;\n"
"    background-position: center center;\n"
"    border:none;\n"
"}\n"
"QPushButton:hover\n"
"{\n"
"    background-image:url(:/icons/ui_icons/substract (1).png);\n"
"}")
        self.btn_del_pic.setText("")
        self.btn_del_pic.setFlat(False)
        self.btn_del_pic.setObjectName("btn_del_pic")
        self.horizontalLayout_3.addWidget(self.btn_del_pic)
        self.label_3 = QtWidgets.QLabel(self.tab_pices)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setStyleSheet("color:rgb(161, 88, 255)")
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.hs_zoom = QtWidgets.QSlider(self.tab_pices)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.hs_zoom.sizePolicy().hasHeightForWidth())
        self.hs_zoom.setSizePolicy(sizePolicy)
        self.hs_zoom.setOrientation(QtCore.Qt.Horizontal)
        self.hs_zoom.setObjectName("hs_zoom")
        self.horizontalLayout_3.addWidget(self.hs_zoom)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
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
        self.label_2.setText(_translate("MainWindow", "范围"))
        self.cb_dsm_search_kind.setStatusTip(_translate("MainWindow", "VideoStation资料库"))
        self.label.setText(_translate("MainWindow", "关键字"))
        self.edt_dsm_search_keyword.setStatusTip(_translate("MainWindow", "输入关键字查找(留空表示显示当前资料库全部视频)"))
        self.edt_dsm_search_keyword.setPlaceholderText(_translate("MainWindow", "输入关键字查找(留空表示显示全部视频)"))
        self.chk_only_nil.setText(_translate("MainWindow", "只查找无海报视频"))
        self.btn_dsm_search.setStatusTip(_translate("MainWindow", "查找VideoStation视频"))
        self.btn_setting.setStatusTip(_translate("MainWindow", "设置"))
        self.tbl_search_result_widget.setSortingEnabled(True)
        self.cb_current_video.setStatusTip(_translate("MainWindow", "当前修改的视频"))
        self.btn_meta_search.setStatusTip(_translate("MainWindow", "查找当前视频元数据"))
        self.btn_fresh.setStatusTip(_translate("MainWindow", "刷新当前视频元数据"))
        self.btn_save.setStatusTip(_translate("MainWindow", "保存修改结果到VideoStation"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_meta), _translate("MainWindow", "元数据"))
        self.btn_add_pic.setStatusTip(_translate("MainWindow", "添加图片"))
        self.btn_del_pic.setStatusTip(_translate("MainWindow", "删除选中图片"))
        self.label_3.setText(_translate("MainWindow", "可以直接拖入多张图片，前两张图片会写入VideoStation。第一张为海报，第二张为背景；在列表内拖动图片可以调整图片顺序。"))
        self.hs_zoom.setStatusTip(_translate("MainWindow", "缩放图片"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_pices), _translate("MainWindow", "海报"))

from widgets.tbl_edit_metadata import TblMetadata
from widgets.tbl_search_widget import TblSeacheResult
import ui.res.interface_rc
