#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from time import sleep

import requests
from PyQt5.QtCore import pyqtSignal, QEventLoop

from spiders.base_thread import BaseThread
from utils import get_spider_metastruct
from verif_code import VerifCodeDialog


class SearchSpider(BaseThread):
    search_finish = pyqtSignal()
    put_meta = pyqtSignal(dict)
    # get_vercode = pyqtSignal(dict)

    def __init__(self, spider, keyword):
        super().__init__()
        self.keyword = keyword
        self.spider = spider


    def login(self):
        self.spider.spdider_login()


    def run(self):
        if self.stoped:
            self.spider.stop = True
            return

        self.out_msg.emit('[{}]开始搜索……'.format(self.spider.name))
        for meta in self.spider.search(self.keyword):
            if self.stoped: break

            self.put_meta.emit(meta)
            self.out_msg.emit('[{}]找到{}个……'.format(self.spider.name, self.spider.count))

        self.search_finish.emit()


class DitalSpider(BaseThread):
    dital_finish = pyqtSignal()
    put_meta = pyqtSignal(dict)
    put_imagedata = pyqtSignal(bytes)

    def __init__(self, spider, url,meta=None):
        super().__init__()
        self.url = url
        self.spider = spider
        self.meta = get_spider_metastruct()
        if meta:
            self.meta.update(meta)

    def run(self):
        if self.stoped:
            self.spider.stop = True
            return
        self.out_msg.emit('[{}]开始获取元数据……'.format(self.spider.name))
        meta,imgs = self.spider.dital(self.url, self.meta)
        if meta:
            self.put_meta.emit(meta)

        if imgs:

            self.out_msg.emit('[{}]开始下载海报……'.format(self.spider.name))
            for i,each in enumerate(self.spider.get_img_data(imgs)):
                if self.stoped:
                    break
                self.out_msg.emit('[{}]正在下载海报{}……'.format(self.spider.name,i+1))
                self.put_imagedata.emit(each)
                # sleep(0.5)


        self.dital_finish.emit()