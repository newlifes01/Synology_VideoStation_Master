#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: syaofox@gmail.com
import os
from PyQt5.QtCore import QByteArray, QBuffer, QIODevice, QSize, Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QListWidget, QListWidgetItem


class LstEditSearchMetadata(QListWidget):

    def __init__(self, parent=None):
        super(LstEditSearchMetadata, self).__init__(parent)
        # self.setIconSize(QSize(200,200))
        self.setSpacing(5)

        self.setStyleSheet('''
                        QListView::item:selected:!active {
                            background: rgb(255, 222, 21);
                        }
                        QListView::item:selected:active {
                            background: rgb(255, 222, 122);
                        }
                        QListView::item:hover {
                            background: rgb(255, 222, 122);
                        }
                ''')

    def add_pic_fromData(self, data, boshowsize=True):
        if not data:
            return

        pixmap = None
        if isinstance(data, str):
            if os.path.isfile(data):
                pixmap = QPixmap(data)
        elif isinstance(data, bytes):
            pixmap = QPixmap()
            pixmap.loadFromData(data)
        if not pixmap:
            return
        icon = QIcon(pixmap)

        s_size = ''
        if boshowsize:
            s_size = '{}*{}'.format(pixmap.width(), pixmap.height())

        item = QListWidgetItem(icon, self.tr(s_size))
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Checked)
        self.addItem(item)
        self.scrollToItem(item)

    def get_piclist_data_to_dict(self):
        for i in range(self.count()):
            try:
                item = self.item(i)
                if item.checkState() != Qt.Checked:
                    continue
                icon = item.icon()
                if icon:
                    pixmap = icon.pixmap(icon.availableSizes()[0])
                    array = QByteArray()
                    buffer = QBuffer(array)
                    buffer.open(QIODevice.WriteOnly)
                    pixmap.save(buffer, 'JPG')
                    buffer.close()
                    yield array.data()
            except Exception:
                pass