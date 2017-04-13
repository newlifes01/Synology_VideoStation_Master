#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QDialog

from ui.search_metadata_window import Ui_search_meta_Dialog


class SearchMetadataDialog(QDialog, Ui_search_meta_Dialog):
    # login_finished = pyqtSignal(str,str,str)

    def __init__(self):
        super().__init__()
        self.video = None
        self.setupUi(self)
        self.btn_add.setFocus()

        regex = QRegExp("\d+")
        validator = QRegExpValidator(regex)
        self.edt_seasion.setValidator(validator)
        self.edt_episode.setValidator(validator)


        self.btn_tvshow_search.clicked.connect(self.search_meta)

    def open_dialog(self, video):
        if not video:
            return
        else:
            print(video)
            self.video = video
            self.ref_search_info()

            self.exec_()

    def ref_search_info(self):
        if not self.video:
            return

        filename = os.path.splitext(os.path.basename(self.video.get('path')))[0]
        title = self.video.get('title')

        if not filename:
            filename = title


        self.edt_tvshows.setText(filename)
        season = self.video.get('季')
        if season:
            self.edt_seasion.setText(season)

        episode = self.video.get('集')
        if episode:
            self.edt_episode.setText(episode)

    def get_search_info(self):

        return {
            'keyword': self.edt_tvshows.text().strip(),
            'season': self.edt_seasion.text().strip(),
            'episode': self.edt_episode.text().strip(),
        }

    def search_meta(self):
        search_info = self.get_search_info()
        print(search_info)







        #
        #     self.btn_login.clicked.connect(
        #         lambda: self.login_to_dsm(self.edt_ip.text(), self.edt_id.text(), self.edt_psw.text()))
        #
        # def login_to_dsm(self, ip, account, password):
        #     if not ip and not account and not password:
        #         QMessageBox.warning(self, '错误', '登陆失败！', QMessageBox.Ok)
        #         return
        #     self.dsm.ip = ip
        #     if self.dsm.login_dsm(account, password):
        #         self.accept()
        #     else:
        #         QMessageBox.warning(self, '错误', '登陆失败！', QMessageBox.Ok)
        #         return

        # dsm = DSMAPI(self.session, ip)
        # if dsm.login(account, password):
        #     self.login_finished.emit({'ip':ip,'account':account,'password':password,'cookies':requests.utils.dict_from_cookiejar(self.session.cookies)})
        #     self.accept()
        # else:
        #     QMessageBox.warning(self, '错误', '登陆失败！', QMessageBox.Ok)
