#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPainter
from PyQt5.QtWidgets import QTableWidget, QHeaderView, QTableWidgetItem, QWidget
from collections import OrderedDict

import utils
from widgets.tbl_base import BaseTblSearch


class TblSeacheResult(BaseTblSearch):
    put_meta = pyqtSignal(OrderedDict)

    def __init__(self, parent=None):
        super(TblSeacheResult, self).__init__(parent)
        self.itemClicked.connect(self.item_select)

    def insert_data(self, meta, row=-1):
        if not meta:
            return

        self.item_background = not self.item_background

        title = meta.get('标题')
        if not title:
            title = meta.get('电视节目标题')
        if not title:
            return

        title = utils.get_screen_width(title, max_width=60, tail_length=2)

        icon_data = meta.get('tag').get('poster')
        if not icon_data:
            icon_data = utils.get_res_to_bytes(':/icons/others/empty.png')
        stype = meta.get('tag').get('type')

        summary = meta.get('摘要')

        pixmap = QPixmap()
        pixmap.loadFromData(icon_data)

        if stype == 'home_video':
            icon_width, icon_heigh = utils.HOMEVIEDO_WIDTH, utils.HOMEVIEDO_WIDTH
        else:
            icon_width, icon_heigh = utils.ITEM_WIDTH, utils.ITEM_HEIGHT

        icon = QIcon(pixmap.scaled(icon_width, icon_heigh, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))

        if row >= 0:
            item = self.item(row, 0)
            item.setIcon(icon)

            item = self.item(row, 1)
            item.setText(stype)

            item = self.item(row, 2)
            item.setText(title)

            item = self.item(row, 3)
            item.setText(summary)
        else:
            self.insertRow(0)
            item = self.cell(color=self.item_background)
            item.setIcon(icon)
            item.setSizeHint(QSize(icon_width + 5, icon_heigh))
            self.setItem(0, 0, item)
            item.setData(Qt.UserRole, meta)

            item = self.cell(text=stype, color=self.item_background)
            self.setItem(0, 1, item)

            item = self.cell(text=title, color=self.item_background)
            self.setItem(0, 2, item)

            item = self.cell(text=summary, color=self.item_background)
            self.setItem(0, 3, item)

    def item_select(self, item):
        row = self.currentRow()
        item = self.item(row, 0)
        if item:
            data = item.data(Qt.UserRole)
            self.put_meta.emit(data)
