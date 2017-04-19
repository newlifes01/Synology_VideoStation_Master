#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: syaofox@gmail.com
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QBrush

import utils
from widgets.tbl_search_widget import BaseTblSearch


class TblSeacheMetaResult(BaseTblSearch):
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

            i_width, i_heigh = utils.ITEM_WIDTH, utils.ITEM_HEIGHT
            if meta['tag']['xy']:
                i_width, i_heigh = meta['tag']['xy']

            # icon = QIcon(
            #     pixmap.scaled(i_width, i_heigh, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
            item = self.cell(color=self.item_background)
            # item.setIcon(icon)
            # item.setSizeHint(QSize(i_width + 5, i_heigh))
            pixmap = pixmap.scaled(i_width, i_heigh, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            # self.setImage(0, 0, pixmap)
            # self.setItem(0, 0, item)
            # item.setData(Qt.UserRole, meta)
            # item.setTextAlignment(Qt.AlignCenter)

            item.setData(Qt.DecorationRole,pixmap)
            self.setItem(0, 0, item)

        item = self.cell(text=meta.get('tag').get('video_id'), color=self.item_background)
        item.setData(Qt.UserRole, meta)
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
        item = self.item(row, 1)
        if item:
            data = item.data(Qt.UserRole)
            return data

    def get_select_row_data(self):
        row = self.currentRow()
        item = self.item(row, 1)
        if item:
            data = item.data(Qt.UserRole)
            return data
