#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: syaofox@gmail.com
from PyQt5.QtWidgets import QTableWidget

import utils
from widgets.tbl_edit_metadata import TblMetadata


class TblSearchResultEidt(TblMetadata):

    def __init__(self, parent=None):
        super(TblSearchResultEidt, self).__init__(parent)

    def get_metadata(self,meta=None):



        row = self.rowCount()
        for i in range(0, row):
            key = self.item(i, 0).text()
            value = self.item(i, 1).text()
            if key == '海报':
                continue
            if key == '级别':
                value = utils.get_cert_txt(self.rating_cb.currentIndex())

            meta[key] = value

        return meta