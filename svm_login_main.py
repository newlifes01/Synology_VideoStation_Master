#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QMessageBox
from ui.login_DSM_window import Ui_dsm_login


class LoginDialog(QDialog, Ui_dsm_login):
    def __init__(self, dsm):
        super().__init__()
        self.dsm = dsm
        self.setupUi(self)

        self.btn_login.clicked.connect(
            lambda: self.login_to_dsm(self.edt_ip.text(), self.edt_id.text(), self.edt_psw.text()))

    def login_to_dsm(self, ip, account, password):
        if not ip and not account and not password:
            QMessageBox.warning(self, '错误', '登陆失败！', QMessageBox.Ok)
            return
        self.dsm.ip = ip
        if self.dsm.login_dsm(account, password):
            self.accept()
        else:
            QMessageBox.warning(self, '错误', '登陆失败！', QMessageBox.Ok)
            return