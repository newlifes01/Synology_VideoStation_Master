#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: syaofox@gmail.com
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QHeaderView
from collections import OrderedDict

import utils
from widgets.tbl_search_widget import BaseTblSearch


class TblSeacheMetaResult(BaseTblSearch):
    # put_meta = pyqtSignal(OrderedDict)

    def __init__(self, parent=None):
        super(TblSeacheMetaResult, self).__init__(parent)
        self.itemClicked.connect(self.item_select)

    def insert_data(self, meta):
        if not meta:
            return

        self.item_background = not self.item_background
        icon_data = meta['tag']['poster']
        self.insertRow(0)
        if not icon_data:
            icon_data = utils.get_res_to_bytes(':/icons/others/empty.png')
        if icon_data:
            pixmap = QPixmap()
            pixmap.loadFromData(icon_data)

            icon = QIcon(
                pixmap.scaled(utils.ITEM_WIDTH, utils.ITEM_HEIGHT, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
            item = self.cell(color=self.item_background)

            item.setIcon(icon)
            item.setSizeHint(QSize(utils.ITEM_WIDTH + 5, utils.ITEM_HEIGHT))
            self.setItem(0, 0, item)

            item.setData(Qt.UserRole, meta)

        item = self.cell(text=meta.get('tag').get('video_id'), color=self.item_background)
        self.setItem(0, 1, item)

        title = ''
        if '标题' in meta:
            title = meta['标题']
        if '电视节目标题' in meta:
            title = meta['电视节目标题']
        if '集标题' in meta:
            title = meta['集标题']

        item = self.cell(text=utils.get_screen_width(title, 100), color=self.item_background)
        self.setItem(0, 2, item)

        item = self.cell(text=meta.get('tag').get('tip'), color=self.item_background)
        self.setItem(0, 3, item)

        item = self.cell(text=meta.get('tag').get('dital_url'), color=self.item_background)
        self.setItem(0, 4, item)

    def item_select(self):
        row = self.currentRow()
        item = self.item(row, 0)
        if item:
            data = item.data(Qt.UserRole)
            return data
            # self.put_meta.emit(data)

    def get_select_row_data(self):
        row = self.currentRow()
        item = self.item(row, 0)
        if item:
            data = item.data(Qt.UserRole)
            return data
