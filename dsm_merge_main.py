#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: syaofox@gmail.com
from PyQt5.QtWidgets import QDialog
from ui.dsm_merge_window import Ui_Dialog_dsm_merge


class DSMMerge(QDialog, Ui_Dialog_dsm_merge):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.meth = ''
        self.btn_ok.clicked.connect(self.get_merge_meth)
        self.btn_cancel.clicked.connect(self.reject)


    def get_merge_meth(self):
        if self.rb_skip.isChecked():
            self.meth = 'skip'
        if self.rb_overwrite.isChecked():
            self.meth = 'overwrite'

        self.accept()
