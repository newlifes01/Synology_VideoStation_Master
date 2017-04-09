# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login_DSM_window.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_dsm_login(object):
    def setupUi(self, dsm_login):
        dsm_login.setObjectName("dsm_login")
        dsm_login.resize(275, 167)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(dsm_login.sizePolicy().hasHeightForWidth())
        dsm_login.setSizePolicy(sizePolicy)
        self.gridLayout = QtWidgets.QGridLayout(dsm_login)
        self.gridLayout.setObjectName("gridLayout")
        self.edt_ip = QtWidgets.QLineEdit(dsm_login)
        self.edt_ip.setObjectName("edt_ip")
        self.gridLayout.addWidget(self.edt_ip, 0, 0, 1, 3)
        self.edt_id = QtWidgets.QLineEdit(dsm_login)
        self.edt_id.setObjectName("edt_id")
        self.gridLayout.addWidget(self.edt_id, 1, 0, 1, 3)
        self.edt_psw = QtWidgets.QLineEdit(dsm_login)
        self.edt_psw.setObjectName("edt_psw")
        self.gridLayout.addWidget(self.edt_psw, 2, 0, 1, 3)
        spacerItem = QtWidgets.QSpacerItem(85, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)
        self.btn_login = QtWidgets.QPushButton(dsm_login)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_login.sizePolicy().hasHeightForWidth())
        self.btn_login.setSizePolicy(sizePolicy)
        self.btn_login.setObjectName("btn_login")
        self.gridLayout.addWidget(self.btn_login, 3, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(84, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 3, 2, 1, 1)

        self.retranslateUi(dsm_login)
        QtCore.QMetaObject.connectSlotsByName(dsm_login)

    def retranslateUi(self, dsm_login):
        _translate = QtCore.QCoreApplication.translate
        dsm_login.setWindowTitle(_translate("dsm_login", "登陆到VideoStation"))
        self.edt_ip.setPlaceholderText(_translate("dsm_login", "输入SyonlogyIP(192.168.2.2:5000)"))
        self.edt_id.setPlaceholderText(_translate("dsm_login", "输入账号"))
        self.edt_psw.setPlaceholderText(_translate("dsm_login", "输入密码"))
        self.btn_login.setText(_translate("dsm_login", "登陆"))

