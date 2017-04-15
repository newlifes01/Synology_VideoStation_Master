#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from PyQt5.QtCore import QRegExp, Qt, QSize
from PyQt5.QtGui import QRegExpValidator, QIcon, QPixmap
from PyQt5.QtWidgets import QDialog, QMessageBox, QListWidgetItem, QApplication

import utils
from DSM.dsm_video_station import DSMAPI
from spiders.dmm_spider import DmmSpider
from spiders.spider_manager import SearchSpider, DitalSpider
from ui.search_metadata_window import Ui_search_meta_Dialog


class SearchMetadataDialog(QDialog, Ui_search_meta_Dialog):
    def __init__(self):
        super().__init__()
        self.video = None
        self.setupUi(self)
        self.btn_add.setFocus()

        regex = QRegExp("\d+")
        validator = QRegExpValidator(regex)
        self.edt_seasion.setValidator(validator)
        self.edt_episode.setValidator(validator)

        self.btn_search.clicked.connect(self.search_meta)

        self.spider_search_Manager = None
        self.init_spiders('dmm.co.jp', DmmSpider, ':/icons/spider_icons/dmm.ico')

        self.tbl_search_result.put_meta.connect(self.search_meta_item_select)

        self.hs_zoom.setMaximum(200)
        self.hs_zoom.setProperty("value", 100)

        self.hs_zoom.valueChanged.connect(self.pic_zoom)

        self.btn_add.clicked.connect(self.finish_edit)
        self.meta_return = None
        self.pices_return = None





    def init_spiders(self, name, class_seacher=None, icon=""):

        search_spider = class_seacher(name)
        self.cb_spiders.addItem(QIcon(icon), name, search_spider)

    def open_dialog(self, video):
        if not video:
            return
        else:
            self.meta_return = None
            self.pices_return = None
            self.video = video
            self.ref_search_info()



    def ref_search_info(self):
        if not self.video:
            return


        filename = os.path.splitext(os.path.basename(self.video.get('path')))[0]
        title = self.video.get('title')

        if not filename:
            filename = title

        self.edt_keyword.setText(filename)
        season = self.video.get('季')
        if season:
            self.edt_seasion.setText(season)

        episode = self.video.get('集')
        if episode:
            self.edt_episode.setText(episode)

    def get_search_info(self):
        if not self.edt_keyword.text():
            QMessageBox.warning(self, '错误', '关键字不能为空！', QMessageBox.Ok)
            return None

        return {
            'keyword': self.edt_keyword.text().strip(),
            'season': self.edt_seasion.text().strip(),
            'episode': self.edt_episode.text().strip(),
        }

    def pic_zoom(self, value):
        size = 200 * value // 100
        self.lst_pices.setIconSize(QSize(size, size))

    def status_msg(self, msg):
        self.label_tips.setText(msg)

    def add_finded_meta(self, meta):
        self.tbl_search_result.insert_data(meta)

    def spider_search_finish(self, count):
        self.tbl_search_result.setEnabled(True)
        self.btn_search.setText('搜索元数据')
        self.status_msg('完成搜索,共找到{}个结果'.format(count))

    def search_meta(self):
        search_info = self.get_search_info()
        if search_info:
            # 停止搜索
            if self.spider_search_Manager and self.spider_search_Manager.isRunning():
                self.btn_search.setText('搜索元数据')
                self.tbl_search_result.setEnabled(True)
                self.spider_search_Manager.stop_thread()
            else:
                self.tbl_search_result.clear_data(hearders=('海报','番号', '标题', '信息', '地址'))
                spider = self.cb_spiders.currentData(Qt.UserRole)
                spider.clear()

                self.spider_search_Manager = SearchSpider(spider, search_info.get('keyword'))
                self.spider_search_Manager.out_msg.connect(self.status_msg)
                self.spider_search_Manager.put_meta.connect(self.add_finded_meta)

                self.spider_search_Manager.search_finish.connect(self.spider_search_finish)

                self.spider_search_Manager.login()  # 登陆
                # code, ok = VerifCodeDialog.get_VerifCode(data=data)
                # self.spider_search_Manager.set_login_data(code)

                self.spider_search_Manager.start()
                self.btn_search.setText('停止')
                self.tbl_search_result.setEnabled(False)

    def search_meta_item_select(self,meta):
        if meta:
            spider = self.cb_spiders.currentData(Qt.UserRole)
            self.spider_dital_Manager = DitalSpider(spider, meta.get('dital_url'), meta=meta)
            self.spider_dital_Manager.out_msg.connect(self.status_msg)
            self.spider_dital_Manager.put_meta.connect(self.add_detial)
            self.spider_dital_Manager.dital_finish.connect(self.spider_dital_finish)
            # self.spider_dital_Manager.put_imagedata.connect(self.add_detail_images)
            self.spider_dital_Manager.start()

    def spider_dital_finish(self):
        self.status_msg('元数据抓取完成')
        # self.gb_meta_search.setEnabled(True)
        # self.gb_meta_set.setEnabled(True)
        # self.overwrite = True

    def add_detial(self, meta):
        # self.tbl_metadata.set_tbl_content(meta, self.overwrite)#todo feidsm
        self.lst_pices.clear()
        video_dital = utils.search_result_to_table_data(meta,self.video.get('type'))
        poster = meta.get('poster')
        if poster:
            self.lst_pices.add_pic_fromData(poster)
        backdrop = meta.get('backdrop')
        if backdrop:
            self.lst_pices.add_pic_fromData(backdrop)


        self.tbl_metadata.ref_table(video_dital)

    def finish_edit(self):
        self.meta_return = self.tbl_metadata.get_metadata()

        self.pices_return = self.lst_pices.get_piclist_data_to_dict()

        self.accept()





if __name__ == '__main__':
    app = QApplication(sys.argv)
    search_meta_form = SearchMetadataDialog()

    search_meta_form.open_dialog({'title': '風俗嬢', 'path': ''})

    sys.exit(app.exec_())
    # print(result)
