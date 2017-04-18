# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dsm_merge_window.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog_dsm_merge(object):
    def setupUi(self, Dialog_dsm_merge):
        Dialog_dsm_merge.setObjectName("Dialog_dsm_merge")
        Dialog_dsm_merge.resize(392, 145)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dialog_dsm_merge)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(Dialog_dsm_merge)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setStyleSheet("color: rgb(0, 0, 255);")
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(50, -1, 50, -1)
        self.verticalLayout.setSpacing(12)
        self.verticalLayout.setObjectName("verticalLayout")
        self.rb_skip = QtWidgets.QRadioButton(Dialog_dsm_merge)
        self.rb_skip.setObjectName("rb_skip")
        self.verticalLayout.addWidget(self.rb_skip)
        self.rb_overwrite = QtWidgets.QRadioButton(Dialog_dsm_merge)
        self.rb_overwrite.setChecked(True)
        self.rb_overwrite.setObjectName("rb_overwrite")
        self.verticalLayout.addWidget(self.rb_overwrite)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btn_ok = QtWidgets.QPushButton(Dialog_dsm_merge)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_ok.sizePolicy().hasHeightForWidth())
        self.btn_ok.setSizePolicy(sizePolicy)
        self.btn_ok.setObjectName("btn_ok")
        self.horizontalLayout.addWidget(self.btn_ok)
        self.btn_cancel = QtWidgets.QPushButton(Dialog_dsm_merge)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_cancel.sizePolicy().hasHeightForWidth())
        self.btn_cancel.setSizePolicy(sizePolicy)
        self.btn_cancel.setObjectName("btn_cancel")
        self.horizontalLayout.addWidget(self.btn_cancel)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog_dsm_merge)
        QtCore.QMetaObject.connectSlotsByName(Dialog_dsm_merge)

    def retranslateUi(self, Dialog_dsm_merge):
        _translate = QtCore.QCoreApplication.translate
        Dialog_dsm_merge.setWindowTitle(_translate("Dialog_dsm_merge", "视频信息冲突"))
        self.label.setText(_translate("Dialog_dsm_merge", "已经在同名视频，请选择："))
        self.rb_skip.setText(_translate("Dialog_dsm_merge", "保留(合并2个视频并使用老的视频信息)"))
        self.rb_overwrite.setText(_translate("Dialog_dsm_merge", "替换(合并2个视频并使用新的视频信息)"))
        self.btn_ok.setText(_translate("Dialog_dsm_merge", "执行"))
        self.btn_cancel.setText(_translate("Dialog_dsm_merge", "放弃"))

