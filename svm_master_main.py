#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests

import utils
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel

from DSM.dsm_video_station import DSMAPI
from svm_login_main import LoginDialog
from ui.main_window import Ui_MainWindow


class MainForm(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)
        self.setupUi(self)
        self.initUi()

        # DSM参数
        self.session = requests.session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'})

        self.DSM = DSMAPI(self.session, '')


        # self.login_form.login_finished.connect(self.login_finished)

    def initUi(self):
        self.toolBox.setCurrentIndex(0)
        self.page_metadata.setEnabled(False)
        self.page_about.setEnabled(False)

        self.lb_dsm_status_cap = QLabel('DSM状态:')
        self.status_bar.addPermanentWidget(self.lb_dsm_status_cap)

        self.lb_dsm_status = QLabel('未登陆')
        self.status_bar.addPermanentWidget(self.lb_dsm_status)

    def login_finished(self, ip, account, password):
        self.DSM.ip = ip
        self.DSM.login_dsm(account, password)

    def check_login_status(self):
        if not self.DSM.check_login_status():
            self.login_form = LoginDialog(self.DSM)
            if not self.login_form.exec_():
                sys.exit(0)
            else:
                return True
        else:
            return True



if __name__ == '__main__':
    app = QApplication(sys.argv)
    print(utils.CACHE_PATH, utils.CONFIG_PATH)
    main_form = MainForm()
    main_form.show()
    main_form.check_login_status()
    main_form.lb_dsm_status.setText('已登陆')

    sys.exit(app.exec_())
