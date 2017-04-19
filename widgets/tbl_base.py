#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: syaofox@gmail.com
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPainter, QFont, QColor
from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox

import utils


class ImageWidget(QWidget):
    def __init__(self, image_data, parent):
        super(ImageWidget, self).__init__(parent)
        self.picture = image_data


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.picture)

class BaseTblSearch(QTableWidget):
    def __init__(self, parent=None):
        super(BaseTblSearch, self).__init__(parent)

        self.item_background = True
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

        self.horizontalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)

    # 创建表格列表框
    def genCombobox(self, data):
        widget = QComboBox()
        font = QFont()
        font.setPointSize(11)
        widget.setFont(font)
        for each in data:
            for k, v in each.items():
                widget.addItem(k, v)

        widget.setCurrentIndex(0)
        widget.setFixedHeight(22)
        return widget

    def setImage(self, row, col, image_data):
        image = ImageWidget(image_data, self)
        self.setCellWidget(row, col, image)



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

    def clear_data(self, hearders=('海报', '种类', '标题', '简介')):
        self.horizontalHeader().setVisible(True)
        self.horizontalHeader().setHighlightSections(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.verticalHeader().setDefaultSectionSize(utils.ITEM_HEIGHT)
        self.clear()
        self.setRowCount(0)

        self.setColumnCount(len(hearders))
        self.setHorizontalHeaderLabels(hearders)