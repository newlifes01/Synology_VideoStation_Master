#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker


class BaseThread(QThread):

    out_msg = pyqtSignal(str)  # 显示信息

    def __init__(self):
        super().__init__()
        self.mutex = QMutex()
        self.stoped = False

    def thread_init(self, keyword=''):
        self.stoped = False
        with QMutexLocker(self.mutex):
            self.stoped = False

    def stop_thread(self):
        with QMutexLocker(self.mutex):
            self.stoped = True

    def isStoped(self):
        with QMutexLocker(self.mutex):
            return self.stoped

    def run(self):
        pass