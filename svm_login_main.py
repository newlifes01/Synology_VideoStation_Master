#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QMessageBox

from ui.login_DSM_window import Ui_dsm_login


class LoginDialog(QDialog, Ui_dsm_login):
    # login_finished = pyqtSignal(str,str,str)

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

            # dsm = DSMAPI(self.session, ip)
            # if dsm.login(account, password):
            #     self.login_finished.emit({'ip':ip,'account':account,'password':password,'cookies':requests.utils.dict_from_cookiejar(self.session.cookies)})
            #     self.accept()
            # else:
            #     QMessageBox.warning(self, '错误', '登陆失败！', QMessageBox.Ok)
