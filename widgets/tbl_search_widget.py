#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor
from PyQt5.QtWidgets import QTableWidget, QHeaderView, QTableWidgetItem

import utils


class TblSeacheResult(QTableWidget):
    put_meta = pyqtSignal(dict)

    def __init__(self, parent=None):
        super(TblSeacheResult, self).__init__(parent)
        self.item_background = True
        self.clear_data()
        self.setIconSize(QSize(utils.ITEM_WIDTH - 2, utils.ITEM_HEIGHT - 2))

        self.setStyleSheet('''
                        QTableWidget::item{
                            selection-background-color: #ACD6FF;
                            selection-color :white;
                        }
                        QTableWidget::item:hover
                        {
                           background-color: #ACD6FF;
                        }
                       
                        # QTableWidget::item:selected:!active {
                        #     background: rgb(255, 222, 21);
                        # }
                        # QTableWidget::item:selected:active {
                        #     background: rgb(255, 222, 122);
                        # }
                        # QTableWidget::item:hover {
                        #     background: rgb(255, 222, 122);
                        # }
                ''')

        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.verticalHeader().setDefaultSectionSize(utils.ITEM_HEIGHT)
        self.setHorizontalHeaderLabels(('海报', '种类', '标题', '简介'))

        self.itemClicked.connect(self.item_select)

    # 设置单元格信息
    def cell(self, editable=True, text="", color=False, align=True):
        item = QTableWidgetItem()
        font = QFont()
        font.setPointSize(11)
        item.setFont(font)
        item.setText(text)
        if not editable:
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            if align:
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignRight)
        if color:
            item.setBackground(QColor(244, 244, 244))

        return item

    def clear_data(self):
        self.clear()
        self.setRowCount(0)
        self.setColumnCount(4)

    def insert_data(self, meta,row=-1):
        if not meta:
            return

        self.setHorizontalHeaderLabels(('海报', '种类', '标题', '简介'))
        self.item_background = not self.item_background
        icon_data = meta['poster']

        stype = meta.get('type')



        if row >= 0 :
            title = utils.get_screen_width(meta.get('标题'), max_width=60, tail_length=2)
            summary = meta.get('摘要')
            if not title:
                return
            if icon_data:
                pixmap = QPixmap()
                pixmap.loadFromData(meta['poster'])

                if stype == 'home_video':
                    icon_width, icon_heigh = utils.HOMEVIEDO_WIDTH, utils.HOMEVIEDO_WIDTH
                else:
                    icon_width, icon_heigh = utils.ITEM_WIDTH, utils.ITEM_HEIGHT

                icon = QIcon(pixmap.scaled(icon_width, icon_heigh, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
                item = self.item(row, 0)
                item.setIcon(icon)

            item = self.item(row, 1)
            item.setText(stype)

            item = self.item(row, 2)
            item.setText(title)

            item = self.item(row, 3)
            item.setText(summary)

        else:
            title = utils.get_screen_width(meta.get('title'), max_width=60, tail_length=2)
            summary = meta.get('summary')
            if not title:
                return
            self.insertRow(0)
            if icon_data:
                pixmap = QPixmap()
                pixmap.loadFromData(meta['poster'])

                if stype == 'home_video':
                    icon_width, icon_heigh = utils.HOMEVIEDO_WIDTH, utils.HOMEVIEDO_WIDTH
                else:
                    icon_width, icon_heigh = utils.ITEM_WIDTH, utils.ITEM_HEIGHT

                icon = QIcon(pixmap.scaled(icon_width, icon_heigh, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
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
            print(data)
            self.put_meta.emit(data)
