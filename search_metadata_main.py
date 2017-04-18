#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from PyQt5.QtCore import QRegExp, Qt, QSize
from PyQt5.QtGui import QRegExpValidator, QIcon, QPixmap
from PyQt5.QtWidgets import QDialog, QMessageBox, QListWidgetItem, QApplication

import utils
from DSM.dsm_video_station import DSMAPI
from spiders.data18_spider import Data18Spider
from spiders.dmm_spider import DmmSpider
from spiders.spider_manager import SearchSpider, DitalSpider
from ui.search_metadata_window import Ui_search_meta_Dialog


class SearchMetadataDialog(QDialog, Ui_search_meta_Dialog):
    def __init__(self):
        super().__init__()
        self.video = None
        self.setupUi(self)
        self.btn_search.setFocus()

        regex = QRegExp("\d+")
        validator = QRegExpValidator(regex)
        self.edt_seasion.setValidator(validator)
        self.edt_episode.setValidator(validator)

        self.btn_search.clicked.connect(self.search_meta)

        self.spider_search_Manager = None
        self.spider_dital_Manager = None
        self.init_spiders('dmm.co.jp', DmmSpider, ':/icons/spider_icons/dmm.ico')
        self.init_spiders('data18.com', Data18Spider, ':/icons/spider_icons/data18.bmp')

        # self.tbl_search_result.put_meta.connect(self.search_meta_item_select)
        self.btn_dital.clicked.connect(self.search_meta_item_select)

        self.hs_zoom.setMaximum(200)
        self.hs_zoom.setProperty("value", 100)

        self.hs_zoom.valueChanged.connect(self.pic_zoom)

        self.btn_add.clicked.connect(self.finish_edit)
        self.btn_cancel.clicked.connect(self.reject)
        self.meta_return = None
        self.pices_return = None
        self.spider_idx =-1

        self.btn_select_all.clicked.connect(lambda :self.lst_pices.choose_pic(1))
        self.btn_unselect_all.clicked.connect(lambda: self.lst_pices.choose_pic(2))

    def init_spiders(self, name, class_seacher=None, icon=""):

        search_spider = class_seacher(name)
        self.cb_spiders.addItem(QIcon(icon), name, search_spider)

    def closeEvent(self, event):

        if self.spider_search_Manager and self.spider_search_Manager.isRunning:
            self.spider_search_Manager.stop_thread()

        if self.spider_dital_Manager and self.spider_dital_Manager.isRunning:
            self.spider_dital_Manager.stop_thread()

        self.spider_idx = self.cb_spiders.currentIndex()

        super().closeEvent(event)


    def set_objects_enable(self, step):
        if step == 'false':
            self.groupBoxsetEnabled(False)
            self.tbl_search_result.setEnabled(False)
            self.tabwidget_metas.setEnabled(False)
            self.btn_dital.setEnabled(False)
            self.btn_add.setEnabled(False)
            self.btn_search.setEnabled(False)

        if step == 'searching':
            self.edt_keyword.setEnabled(False)
            self.edt_episode.setEnabled(False)
            self.edt_seasion.setEnabled(False)
            self.cb_spiders.setEnabled(False)
            self.tbl_search_result.setEnabled(False)
            self.btn_dital.setEnabled(False)
            self.tabwidget_metas.setEnabled(False)
            self.btn_add.setEnabled(False)
            self.btn_search.setEnabled(False)

            self.btn_search.setEnabled(True)

        if step == 'searched':
            self.edt_keyword.setEnabled(True)
            self.edt_episode.setEnabled(True)
            self.edt_seasion.setEnabled(True)
            self.cb_spiders.setEnabled(True)
            self.tbl_search_result.setEnabled(True)
            self.btn_dital.setEnabled(True)
            self.tabwidget_metas.setEnabled(False)

            self.btn_search.setEnabled(True)

        if step == 'ditaling':
            self.groupBox.setEnabled(False)
            self.tbl_search_result.setEnabled(False)
            self.tbl_metadata.setEnabled(False)
            self.lst_pices.setEnabled(False)
            self.hs_zoom.setEnabled(False)
            self.btn_add.setEnabled(False)
            self.btn_cancel.setEnabled(False)

            self.tabwidget_metas.setEnabled(True)
            self.btn_dital.setEnabled(True)

        if step == 'ditaled':
            self.groupBox.setEnabled(True)
            self.tbl_search_result.setEnabled(True)
            self.tbl_metadata.setEnabled(True)
            self.lst_pices.setEnabled(True)
            self.hs_zoom.setEnabled(True)
            self.btn_add.setEnabled(True)
            self.btn_cancel.setEnabled(True)
            self.tabwidget_metas.setEnabled(True)
            self.btn_dital.setEnabled(True)

        self.app.processEvents()


    def open_dialog(self, video,app,spider_idx):
        if not video:
            return
        else:
            self.meta_return = None
            self.pices_return = None
            self.video = video
            self.app = app
            self.ref_search_info(spider_idx)

    def ref_search_info(self,spider_idx):
        if not self.video:
            return

        filename = os.path.splitext(self.video.get('文件名'))[0]

        if not filename:
            title = self.video.get('标题')
            if not title:
                title = self.video.get('电视节目标题')
            filename = title

        self.edt_keyword.setText(filename)
        season = self.video.get('季')
        if season:
            self.edt_seasion.setText(season)

        episode = self.video.get('集')
        if episode:
            self.edt_episode.setText(episode)

        if spider_idx >= 0:
            self.cb_spiders.setCurrentIndex(spider_idx)

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
        # self.tbl_search_result.setEnabled(True)
        self.set_objects_enable('searched')
        self.btn_search.setText('搜索元数据')
        self.status_msg('完成搜索,共找到{}个结果'.format(count))

    def search_meta(self):
        search_info = self.get_search_info()
        if search_info:
            # 停止搜索
            if self.spider_search_Manager and self.spider_search_Manager.isRunning():
                self.btn_search.setText('搜索元数据')
                # self.tbl_search_result.setEnabled(True)
                self.set_objects_enable('searched')
                self.spider_search_Manager.stop_thread()
            else:
                self.btn_search.setText('停止')
                self.set_objects_enable('searching')


                self.tbl_search_result.clear_data(hearders=('海报', '番号', '标题', '信息', '地址'))
                spider = self.cb_spiders.currentData(Qt.UserRole)
                spider.clear()

                self.spider_search_Manager = SearchSpider(spider, search_info.get('keyword'))
                self.spider_search_Manager.out_msg.connect(self.status_msg)
                self.spider_search_Manager.put_meta.connect(self.add_finded_meta)
                self.spider_search_Manager.search_finish.connect(self.spider_search_finish)
                self.spider_search_Manager.login()  # 登陆
                self.spider_search_Manager.start()

                # self.tbl_search_result.setEnabled(False)

    def search_meta_item_select(self):
        meta = self.tbl_search_result.item_select()
        if meta:
            if self.spider_dital_Manager and self.spider_dital_Manager.isRunning():
                self.btn_dital.setText('分析')
                self.set_objects_enable('ditaled')
                # self.tbl_metadata.setEnabled(True)
                self.spider_dital_Manager.stop_thread()
            else:
                spider = self.cb_spiders.currentData(Qt.UserRole)
                self.spider_dital_Manager = DitalSpider(spider, meta.get('tag').get('dital_url'), meta=meta)
                self.spider_dital_Manager.out_msg.connect(self.status_msg)
                self.spider_dital_Manager.put_meta.connect(self.add_detial)
                self.spider_dital_Manager.dital_finish.connect(self.spider_dital_finish)
                self.spider_dital_Manager.put_imagedata.connect(self.add_detail_images)
                self.spider_dital_Manager.start()
                self.btn_dital.setText('停止')
                self.set_objects_enable('ditaling')
                # self.tbl_metadata.setEnabled(False)

    def spider_dital_finish(self):
        self.status_msg('元数据抓取完成')
        self.btn_dital.setText('分析')
        self.set_objects_enable('ditaled')
        # self.tbl_metadata.setEnabled(True)
        self.tbl_metadata.setFocus()

    def add_detail_images(self, img):
        self.lst_pices.add_pic_fromData(img)

    def add_detial(self, meta):
        if not meta:
            return
        self.lst_pices.clear()
        poster = meta.get('tag').get('poster')
        if poster:
            self.lst_pices.add_pic_fromData(poster)
        backdrop = meta.get('tag').get('backdrop')
        if backdrop:
            self.lst_pices.add_pic_fromData(backdrop)

        self.tbl_metadata.ref_table(meta, ignore=['文件名'])

    def finish_edit(self):
        try:
            filename = self.video.get('文件名')
            self.meta_return = self.tbl_metadata.get_metadata(self.tbl_search_result.get_select_row_data())
            self.meta_return['文件名'] = filename
            self.pices_return = self.lst_pices.get_piclist_data_to_dict()


            self.accept()
        except Exception:
            self.reject()
