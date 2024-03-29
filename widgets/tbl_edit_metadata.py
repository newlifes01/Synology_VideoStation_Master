#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QColor, QBrush
from PyQt5.QtWidgets import QTableWidget, QComboBox, QTableWidgetItem, QHeaderView

import utils

# !/usr/bin/env python3
# -*- coding: utf-8 -*-
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QColor, QBrush
from PyQt5.QtWidgets import QTableWidget, QComboBox, QTableWidgetItem, QHeaderView

import utils
from widgets.tbl_base import BaseTblSearch


class TblMetadata(BaseTblSearch):
    out_msg = pyqtSignal(str)

    def __init__(self, parent=None):
        super(TblMetadata, self).__init__(parent)
        # self.setColumnCount(2)
        #
        # self.horizontalHeader().setStretchLastSection(True)
        # self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # self.verticalHeader().setDefaultSectionSize(15)
        # self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def clear_data(self, hearders=('项目', '内容')):

        self.horizontalHeader().setVisible(True)
        self.horizontalHeader().setHighlightSections(True)

        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.verticalHeader().setDefaultSectionSize(15)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.clear()
        self.setRowCount(0)
        self.setColumnCount(len(hearders))
        self.setHorizontalHeaderLabels(hearders)

    # def clear_table(self):
    #     self.clear()
    #     self.setRowCount(0)
    #     self.setColumnCount(2)

    # # 设置单元格信息
    # def cell(self, editable=True, var="", color=None, align=True):
    #     item = QTableWidgetItem()
    #     font = QFont()
    #     font.setPointSize(11)
    #     item.setFont(font)
    #     item.setText(var)
    #     if not editable:
    #         item.setFlags(item.flags() ^ Qt.ItemIsEditable)
    #         if align:
    #             item.setTextAlignment(Qt.AlignCenter | Qt.AlignRight)
    #     if color:
    #         item.setBackground(color)
    #
    #     return item

    def modifiy_table(self, video, ignore=None):
        if not video:
            return

        for row in range(0, self.rowCount()):
            item_k = self.item(row, 0)
            item_v = self.item(row, 1)
            if item_k.text() == '级别':
                certificate = video.get(item_k.text())
                if certificate:
                    cb_cert_idx = utils.get_cert_idx(certificate)
                    self.rating_cb.setCurrentIndex(cb_cert_idx)

            if item_k and item_v:
                str = video.get(item_k.text())
                if str:
                    item_v.setText(str)

    def ref_table(self, video, ignore=None):
        if not video:
            return
        self.clear_data()
        self.rating_cb = self.genCombobox(utils.get_rating_lst())

        certificate = video.get('级别', '')
        cb_cert_idx = -1
        if certificate:
            cb_cert_idx = utils.get_cert_idx(certificate)

        self.setRowCount(0)
        self.setColumnCount(2)

        count = 0
        for k, v in video.items():
            if k == 'tag':
                continue

            if ignore:
                if k in ignore:
                    continue

            isColor = count % 2 == 0

            self.insertRow(self.rowCount())
            item_k = self.cell(editable=False, text=k, color=True if isColor else None)
            item_k.setForeground(QBrush(QColor(0, 149, 225)))
            self.setItem(self.rowCount() - 1, 0, item_k)
            if k == '文件名':
                item_v = self.cell(editable=False, text=v, color=True if isColor else None, align=False)
            else:
                item_v = self.cell(text=v, color=True if isColor else None)

            self.setItem(self.rowCount() - 1, 1, item_v)

            if k == '级别':
                self.setCellWidget(self.rowCount() - 1, 1, self.rating_cb)
                self.rating_cb.setCurrentIndex(cb_cert_idx)

            count += 1

    def get_title(self):
        item = self.item(1, 1)
        if item:
            return item.text()

    def get_metadata(self, meta):
        row = self.rowCount()
        for i in range(0, row):
            key = self.item(i, 0).text()
            value = self.item(i, 1).text()
            if key == '海报':
                continue
            if key == '级别':
                value = utils.get_cert_txt(self.rating_cb.currentIndex())

            meta[key] = value.replace('"', r'\"')

        return meta

#
#
# class TblMetadata(QTableWidget):
#     out_msg = pyqtSignal(str)
#
#     def __init__(self, parent=None):
#         super(TblMetadata, self).__init__(parent)
#         self.setColumnCount(2)
#
#         self.horizontalHeader().setStretchLastSection(True)
#         self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
#         self.verticalHeader().setDefaultSectionSize(15)
#         self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
#
#     # 创建表格列表框
#     def genCombobox(self, data):
#         widget = QComboBox()
#         font = QFont()
#         font.setPointSize(11)
#         widget.setFont(font)
#         for each in data:
#             for k, v in each.items():
#                 widget.addItem(k, v)
#
#         widget.setCurrentIndex(0)
#         widget.setFixedHeight(22)
#         return widget
#
#     def clear_table(self):
#         self.clear()
#         self.setRowCount(0)
#         self.setColumnCount(2)
#
#     # 设置单元格信息
#     def cell(self, editable=True, var="", color=None, align=True):
#         item = QTableWidgetItem()
#         font = QFont()
#         font.setPointSize(11)
#         item.setFont(font)
#         item.setText(var)
#         if not editable:
#             item.setFlags(item.flags() ^ Qt.ItemIsEditable)
#             if align:
#                 item.setTextAlignment(Qt.AlignCenter | Qt.AlignRight)
#         if color:
#             item.setBackground(color)
#
#         return item
#
#     def modifiy_table(self, video, ignore=None):
#         if not video:
#             return
#
#         for row in range(0, self.rowCount()):
#             item_k = self.item(row, 0)
#             item_v = self.item(row, 1)
#             if item_k.text() == '级别':
#                 certificate = video.get(item_k.text())
#                 if certificate:
#                     cb_cert_idx = utils.get_cert_idx(certificate)
#                     self.rating_cb.setCurrentIndex(cb_cert_idx)
#
#             if item_k and item_v:
#                 str = video.get(item_k.text())
#                 if str:
#                     item_v.setText(str)
#
#     def ref_table(self, video, ignore=None):
#         if not video:
#             return
#         self.clear()
#         self.rating_cb = self.genCombobox(utils.get_rating_lst())
#
#         certificate = video.get('级别', '')
#         cb_cert_idx = -1
#         if certificate:
#             cb_cert_idx = utils.get_cert_idx(certificate)
#
#         self.setRowCount(0)
#         self.setColumnCount(2)
#
#         count = 0
#         for k, v in video.items():
#             if k == 'tag':
#                 continue
#
#             if ignore:
#                 if k in ignore:
#                     continue
#
#             isColor = count % 2 == 0
#
#             self.insertRow(self.rowCount())
#             item_k = self.cell(editable=False, var=k, color=QColor(244, 244, 244) if isColor else None)
#             item_k.setForeground(QBrush(QColor(0, 149, 225)))
#             self.setItem(self.rowCount() - 1, 0, item_k)
#             if k == '文件名':
#                 item_v = self.cell(editable=False, var=v, color=QColor(244, 244, 244) if isColor else None, align=False)
#             else:
#                 item_v = self.cell(var=v, color=QColor(244, 244, 244) if isColor else None)
#
#             self.setItem(self.rowCount() - 1, 1, item_v)
#
#             if k == '级别':
#                 self.setCellWidget(self.rowCount() - 1, 1, self.rating_cb)
#                 self.rating_cb.setCurrentIndex(cb_cert_idx)
#
#             count += 1
#
#     def get_title(self):
#         item = self.item(1, 1)
#         if item:
#             return item.text()
#
#     def get_metadata(self, meta):
#         row = self.rowCount()
#         for i in range(0, row):
#             key = self.item(i, 0).text()
#             value = self.item(i, 1).text()
#             if key == '海报':
#                 continue
#             if key == '级别':
#                 value = utils.get_cert_txt(self.rating_cb.currentIndex())
#
#             meta[key] = value.replace('"', r'\"')
#
#         return meta
