# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'search_metadata_window.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_search_meta_Dialog(object):
    def setupUi(self, search_meta_Dialog):
        search_meta_Dialog.setObjectName("search_meta_Dialog")
        search_meta_Dialog.resize(915, 912)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(search_meta_Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox = QtWidgets.QGroupBox(search_meta_Dialog)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setSpacing(12)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMinimumSize(QtCore.QSize(39, 21))
        self.label_2.setMaximumSize(QtCore.QSize(39, 21))
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_4.addWidget(self.label_2)
        self.edt_tvshows = QtWidgets.QLineEdit(self.groupBox)
        self.edt_tvshows.setClearButtonEnabled(True)
        self.edt_tvshows.setObjectName("edt_tvshows")
        self.horizontalLayout_4.addWidget(self.edt_tvshows)
        self.btn_tvshow_search = QtWidgets.QPushButton(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_tvshow_search.sizePolicy().hasHeightForWidth())
        self.btn_tvshow_search.setSizePolicy(sizePolicy)
        self.btn_tvshow_search.setObjectName("btn_tvshow_search")
        self.horizontalLayout_4.addWidget(self.btn_tvshow_search)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setSpacing(12)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_5.addWidget(self.label_3)
        self.edt_seasion = QtWidgets.QLineEdit(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edt_seasion.sizePolicy().hasHeightForWidth())
        self.edt_seasion.setSizePolicy(sizePolicy)
        self.edt_seasion.setMinimumSize(QtCore.QSize(41, 21))
        self.edt_seasion.setMaximumSize(QtCore.QSize(41, 21))
        self.edt_seasion.setObjectName("edt_seasion")
        self.horizontalLayout_5.addWidget(self.edt_seasion)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_5.addWidget(self.label_4)
        self.edt_episode = QtWidgets.QLineEdit(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edt_episode.sizePolicy().hasHeightForWidth())
        self.edt_episode.setSizePolicy(sizePolicy)
        self.edt_episode.setMinimumSize(QtCore.QSize(41, 21))
        self.edt_episode.setMaximumSize(QtCore.QSize(41, 21))
        self.edt_episode.setObjectName("edt_episode")
        self.horizontalLayout_5.addWidget(self.edt_episode)
        self.cb_tvshow_spiders = QtWidgets.QComboBox(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cb_tvshow_spiders.sizePolicy().hasHeightForWidth())
        self.cb_tvshow_spiders.setSizePolicy(sizePolicy)
        self.cb_tvshow_spiders.setObjectName("cb_tvshow_spiders")
        self.horizontalLayout_5.addWidget(self.cb_tvshow_spiders)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.lst_result = QtWidgets.QListWidget(search_meta_Dialog)
        self.lst_result.setObjectName("lst_result")
        self.verticalLayout_2.addWidget(self.lst_result)
        self.tabwidget_metas = QtWidgets.QTabWidget(search_meta_Dialog)
        self.tabwidget_metas.setObjectName("tabwidget_metas")
        self.tab_metadata = QtWidgets.QWidget()
        self.tab_metadata.setObjectName("tab_metadata")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.tab_metadata)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.tbl_metadata = QtWidgets.QTableWidget(self.tab_metadata)
        self.tbl_metadata.setObjectName("tbl_metadata")
        self.tbl_metadata.setColumnCount(0)
        self.tbl_metadata.setRowCount(0)
        self.horizontalLayout_2.addWidget(self.tbl_metadata)
        self.tabwidget_metas.addTab(self.tab_metadata, "")
        self.tab_pices = QtWidgets.QWidget()
        self.tab_pices.setObjectName("tab_pices")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.tab_pices)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.lst_pices = QtWidgets.QListWidget(self.tab_pices)
        self.lst_pices.setObjectName("lst_pices")
        self.horizontalLayout_3.addWidget(self.lst_pices)
        self.tabwidget_metas.addTab(self.tab_pices, "")
        self.verticalLayout_2.addWidget(self.tabwidget_metas)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(538, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btn_add = QtWidgets.QPushButton(search_meta_Dialog)
        self.btn_add.setObjectName("btn_add")
        self.horizontalLayout.addWidget(self.btn_add)
        self.btn_cancel = QtWidgets.QPushButton(search_meta_Dialog)
        self.btn_cancel.setObjectName("btn_cancel")
        self.horizontalLayout.addWidget(self.btn_cancel)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout_2.setStretch(1, 2)
        self.verticalLayout_2.setStretch(2, 4)

        self.retranslateUi(search_meta_Dialog)
        self.tabwidget_metas.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(search_meta_Dialog)

    def retranslateUi(self, search_meta_Dialog):
        _translate = QtCore.QCoreApplication.translate
        search_meta_Dialog.setWindowTitle(_translate("search_meta_Dialog", "搜索元数据"))
        self.label_2.setText(_translate("search_meta_Dialog", "关键字"))
        self.edt_tvshows.setPlaceholderText(_translate("search_meta_Dialog", "输入搜索关键字"))
        self.btn_tvshow_search.setText(_translate("search_meta_Dialog", "搜索"))
        self.label_3.setText(_translate("search_meta_Dialog", "季"))
        self.label_4.setText(_translate("search_meta_Dialog", "集"))
        self.tabwidget_metas.setTabText(self.tabwidget_metas.indexOf(self.tab_metadata), _translate("search_meta_Dialog", "元数据"))
        self.tabwidget_metas.setTabText(self.tabwidget_metas.indexOf(self.tab_pices), _translate("search_meta_Dialog", "海报"))
        self.btn_add.setText(_translate("search_meta_Dialog", "添加"))
        self.btn_cancel.setText(_translate("search_meta_Dialog", "取消"))

import ui.res.interface_rc
