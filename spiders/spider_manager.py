#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from urllib.parse import urljoin

import os
from PyQt5.QtCore import pyqtSignal

import utils
from spiders.base_thread import BaseThread
from collections import OrderedDict


class SearchSpider(BaseThread):
    search_finish = pyqtSignal(int)
    put_meta = pyqtSignal(OrderedDict)

    def __init__(self, spider, keyword, stype='movie'):
        super().__init__()
        self.stype = stype
        self.keyword = keyword
        self.spider = spider

    def login(self):
        self.spider.spdider_login()

    def run(self):
        if self.stoped:
            self.spider.stop = True
            return
        count = 0
        total = 0
        self.out_msg.emit('[{}]开始搜索……'.format(self.spider.name))
        for meta in self.spider.search(self.keyword, self.stype):
            if meta:
                if self.stoped: break



                if isinstance(meta,int):
                    if not total:
                        total = meta
                else:

                    count += 1
                    self.put_meta.emit(meta)

                if total:
                    self.out_msg.emit('[{}]找到{}/{}个……'.format(self.spider.name, count, total))
                else:
                    self.out_msg.emit('[{}]找到{}个……'.format(self.spider.name, count))

        self.search_finish.emit(count)


class DitalSpider(BaseThread):
    dital_finish = pyqtSignal()
    put_meta = pyqtSignal(OrderedDict)
    put_imagedata = pyqtSignal(bytes)

    def __init__(self, spider, url, meta=None):
        super().__init__()
        self.url = url
        self.spider = spider
        self.meta = meta




    def run(self):
        if self.stoped:
            self.spider.stop = True
            return

        self.out_msg.emit('[{}]开始获取元数据……'.format(self.spider.name))
        count = 0
        ditals = self.spider.dital(self.url, self.meta)
        if ditals:
            for each in ditals:
                if self.stoped: break
                if each:
                    if isinstance(each, OrderedDict):
                        self.put_meta.emit(each)
                    if isinstance(each, bytes):
                        count += 1
                        self.out_msg.emit('[{}]正在下载海报{}……'.format(self.spider.name, count))
                        self.put_imagedata.emit(each)

        self.dital_finish.emit()
