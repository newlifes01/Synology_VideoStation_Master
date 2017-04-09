# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'vercode_window.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(213, 176)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.edt_account = QtWidgets.QLineEdit(Dialog)
        self.edt_account.setObjectName("edt_account")
        self.verticalLayout.addWidget(self.edt_account)
        self.edt_psw = QtWidgets.QLineEdit(Dialog)
        self.edt_psw.setObjectName("edt_psw")
        self.verticalLayout.addWidget(self.edt_psw)
        self.lbl_img = QtWidgets.QLabel(Dialog)
        self.lbl_img.setObjectName("lbl_img")
        self.verticalLayout.addWidget(self.lbl_img)
        self.edt_verifcode = QtWidgets.QLineEdit(Dialog)
        self.edt_verifcode.setObjectName("edt_verifcode")
        self.verticalLayout.addWidget(self.edt_verifcode)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 3)
        spacerItem = QtWidgets.QSpacerItem(54, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.btn_ok = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_ok.sizePolicy().hasHeightForWidth())
        self.btn_ok.setSizePolicy(sizePolicy)
        self.btn_ok.setObjectName("btn_ok")
        self.gridLayout.addWidget(self.btn_ok, 1, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(53, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 2, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "登录"))
        self.edt_account.setPlaceholderText(_translate("Dialog", "输入账号"))
        self.edt_psw.setPlaceholderText(_translate("Dialog", "输入密码"))
        self.lbl_img.setText(_translate("Dialog", "验证码"))
        self.edt_verifcode.setToolTip(_translate("Dialog", "输入验证码"))
        self.edt_verifcode.setPlaceholderText(_translate("Dialog", "输入验证码"))
        self.btn_ok.setText(_translate("Dialog", "登陆"))

