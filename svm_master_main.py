#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from time import sleep

import logging
import os
import requests
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QColor

import utils
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QListWidgetItem

from DSM.dsm_video_station import DSMAPI
from models.cache import ConfigCache
from svm_login_main import LoginDialog
from ui.main_window import Ui_MainWindow


class MainForm(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)
        self.setupUi(self)
        self.initUi()
        self.logger = logging.getLogger('MainForm')
        self.show_finished = False
        self.cb_current_video_add_finish = False

        # 配置信息
        self.load_config()
        self.set_config()

        # DSM参数
        self.session = requests.session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'})
        self.DSM = DSMAPI(self.session, '')

        self.dsm_seach_stop = False
        self.dsm_seach_running = False

    def enabel_pages(self, enable):
        self.page_search_DSM.setEnabled(enable[0])
        self.page_metadata.setEnabled(enable[1])
        self.page_about.setEnabled(enable[2])

    def load_config(self):

        self.config = {}
        config = ConfigCache()
        loadconfig = config.get_cache('main_config')
        if loadconfig:
            self.config.update(loadconfig)
        utils.add_log(self.logger, 'info', '读取配置文件：', self.config)

    def set_config(self):
        if self.config:
            self.edt_dsm_search_keyword.setText(self.config.get('dsm_search_keyword', ''))

    def initUi(self):
        self.enabel_pages((0, 0, 0))

        self.lst_dsm_search_result.setSpacing(5)
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

        self.toolBox.setCurrentIndex(0)
        self.page_metadata.setEnabled(False)
        self.page_about.setEnabled(False)

        self.lb_dsm_status_cap = QLabel('DSM状态:')
        self.status_bar.addPermanentWidget(self.lb_dsm_status_cap)

        self.lb_dsm_status = QLabel('未登陆')
        self.status_bar.addPermanentWidget(self.lb_dsm_status)

        self.cb_dsm_search_kind.currentIndexChanged.connect(self.library_selected)
        # self.cb_dsm_search_kind.currentIndexChanged[str].connect(self.library_selected)

        self.btn_dsm_search.clicked.connect(lambda: self.btn_dsm_search_clicked(self.edt_dsm_search_keyword.text()))

        self.lst_dsm_search_result.itemDoubleClicked.connect(self.select_dsm_video)

        self.cb_current_video.currentIndexChanged.connect(self.select_single_video)

    def status_msg(self, msg):
        self.status_bar.showMessage(msg)

    # 检测是否登陆dsm 并登陆
    def check_login_status(self):
        if not self.DSM.check_login_status():
            self.login_form = LoginDialog(self.DSM)
            if not self.login_form.exec_():
                utils.add_log(self.logger, 'info', '登陆失败')
                sys.exit(0)
            else:
                return True
        else:
            return True

    # 获得视频库列表
    def get_dsm_librarys(self):
        libs = self.DSM.get_librarys()
        if not libs: return

        self.cb_dsm_search_kind.addItem(QIcon(':/interface/res/interface/all_video.png'), 'All', libs)

        for lib in libs:

            if lib.get('visible'):
                # lib.update({'title_tip':lib.get('type')})
                self.cb_dsm_search_kind.addItem(QIcon(':/interface/res/interface/{}.png'.format(lib.get('type'))),
                                                lib.get('title'), lib)

        idx = min(self.cb_dsm_search_kind.count(), self.config.get('library_select_idx', 0))
        self.cb_dsm_search_kind.setCurrentIndex(idx)

    def library_selected(self, idx):
        if self.show_finished:
            self.config['library_select_idx'] = idx

    ##### 搜索dsm

    def btn_dsm_search_clicked(self, keyword):
        # todo 全部枚举
        if self.dsm_seach_running:
            self.dsm_seach_stop = True
        else:
            if self.cb_dsm_search_kind.currentIndex() == 0:
                current_librarys = self.cb_dsm_search_kind.currentData(Qt.UserRole)

            else:
                current_librarys = [self.cb_dsm_search_kind.currentData(Qt.UserRole)]

            self.dsm_seach_stop = False
            self.dsm_seach_running = True
            self.lst_dsm_search_result.clear()
            self.lst_dsm_search_result.setEnabled(False)
            self.cb_dsm_search_kind.setEnabled(False)

            total = 0

            self.btn_dsm_search.setIcon(QIcon(':/interface/res/interface/btn_stop.png'))
            self.btn_dsm_search.repaint()
            app.processEvents()

            for current_library in current_librarys:
                if not current_library:
                    return

                if self.dsm_seach_stop:
                    self.dsm_seach_running = False
                    break

                count = self.list_videos(current_library, total, keyword)
                app.processEvents()
                total += count

            self.dsm_seach_running = False
            self.status_msg('[VideoStation搜索]完成！共找到[{}]个,双击选择影片进一步处理'.format(total))
            self.lst_dsm_search_result.setEnabled(True)
            self.cb_dsm_search_kind.setEnabled(True)
            self.btn_dsm_search.setIcon(QIcon(':/interface/res/interface/btn_search.png'))

    def list_videos(self, current_library, total, keyword):
        stype = current_library.get('type')
        sAPI = utils.get_library_API(stype)
        library_id = current_library.get('id')
        count = 0
        self.status_msg('[VideoStation搜索:{}]搜索中……'.format(current_library.get('title')))

        for video in self.DSM.list_videos(library_id, sAPI, stype, keyword):
            if self.dsm_seach_stop:
                self.dsm_seach_running = False
                break
            self.add_dsm_search_result(video)
            count += 1

            self.status_msg('[VideoStation搜索:{}]找到[{}]个'.format(current_library.get('title'), count + total))
            app.processEvents()

        return count

    def add_dsm_search_result(self, dsm_finded):
        if dsm_finded:
            try:
                stype = dsm_finded.get('type')
                pixmap = QPixmap()
                pixmap.loadFromData(dsm_finded['poster'])

                if stype == 'home_video':
                    icon_width, icon_heigh = utils.HOMEVIEDO_WIDTH, utils.HOMEVIEDO_WIDTH
                else:
                    icon_width, icon_heigh = utils.ITEM_WIDTH, utils.ITEM_HEIGHT

                icon = QIcon(
                    pixmap.scaled(icon_width, icon_heigh, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
                title = utils.get_screen_width(dsm_finded.get('title'), max_width=19, tail_length=2)
                if stype == 'tvshow':
                    summary = '{}\n{} 共{}季\n{}'.format(title, dsm_finded.get('type'),
                                                       dsm_finded.get('total_seasons'),
                                                       dsm_finded.get('original_available'))
                else:
                    summary = '{}\n{}\n{}'.format(title, dsm_finded.get('type'),
                                                  dsm_finded.get('original_available'))
                item = QListWidgetItem(icon, summary)
                item.setData(Qt.UserRole, dsm_finded)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
                if stype == 'tvshow':
                    item.setBackground(QColor(255, 222, 222))
                elif stype == 'movie':
                    item.setBackground(QColor(222, 222, 255))
                else:
                    item.setBackground(QColor(222, 225, 222))
                self.lst_dsm_search_result.addItem(item)
                self.lst_dsm_search_result.scrollToBottom()

            except Exception as e:
                utils.add_log(self.logger, 'error', 'add_dsm_search_result', e)

    ####搜索dsm

    #####选择视频
    def select_dsm_video(self, item):
        if item:
            try:
                self.cb_current_video_add_finish = False

                meta = item.data(Qt.UserRole)

                stype = meta.get('type')
                sid = meta.get('id')
                slibrary_id = meta.get('library_id')
                smapper_id = meta.get('mapper_id')

                video = self.DSM.get_video_info(sid, stype)
                if not video:
                    return
                meta_cb = {
                    'type': stype,
                    'id': sid,
                    'library_id': slibrary_id,
                    'mapper_id': smapper_id,
                    'title': video.get('title'),
                    'path': '',
                    'sharepath': '',
                    # 'poster': video.get('poster'),
                }
                file_data = video.get('additional').get('file')
                if file_data:
                    meta_cb.update({
                        'path': video.get('additional').get('file')[0].get('path'),
                        'sharepath': video.get('additional').get('file')[0].get('sharepath'),
                    })


                self.cb_current_video.clear()

                file_name = os.path.basename(meta_cb.get('path'))
                if not file_name:
                    file_name = meta_cb.get('title')

                # self.cb_current_video.setIconSize(QSize(36, 36))
                # poster_data = meta_cb.get('poster')
                # if poster_data:
                #     pixmap = QPixmap()
                #     pixmap.loadFromData(poster_data)
                #     icon = QIcon(pixmap)
                #         # pixmap.scaled(24, 36, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
                # else:
                #     icon = QIcon(':/interface/res/interface/{}.png'.format(stype))

                self.cb_current_video.addItem(QIcon(':/interface/res/interface/{}.png'.format(stype)), file_name, meta_cb)

                if stype == 'tvshow':
                    for episode in self.DSM.get_tvshow_episodes_info(slibrary_id, sid):

                        meta_cb['id'] = episode.get('id')
                        # meta_cb['poster'] = episode.get('poster')

                        file_data = episode.get('additional').get('file')
                        if file_data:
                            meta_cb.update({
                                'path': episode.get('additional').get('file')[0].get('path'),
                                'sharepath': episode.get('additional').get('file')[0].get('sharepath'),
                            })

                        file_name = os.path.basename(meta_cb.get('path'))
                        if not file_name:
                            file_name = '{}.S{}.E{}.{}'.format(episode.get('title'),
                                                               str(episode.get('season')).zfill(2),
                                                               str(episode.get('episode')).zfill(2),
                                                               episode.get('tagline'))

                        # self.cb_current_video.setIconSize(QSize(36, 36))
                        # poster_data = meta_cb.get('poster')
                        # if poster_data:
                        #     pixmap = QPixmap()
                        #     pixmap.loadFromData(poster_data)
                        #     icon = QIcon(pixmap)
                        # else:
                        #     icon = QIcon(':/interface/res/interface/{}.png'.format(stype))

                        self.cb_current_video.addItem(QIcon(':/interface/res/interface/{}.png'.format(stype)), file_name, meta_cb)
                        app.processEvents()
            finally:
                self.page_metadata.setEnabled(True)
                self.toolBox.setCurrentIndex(1)
                self.cb_current_video.setCurrentIndex(-1)
                self.cb_current_video_add_finish = True
                self.cb_current_video.setCurrentIndex(0)

    def select_single_video(self, idx):
        if self.cb_current_video_add_finish:
            self.cb_current_video.currentData(Qt.UserRole)

    # 窗口显示后执行
    def form_showed(self):
        utils.add_log(self.logger, 'info', '检测是否登陆dsm')
        self.check_login_status()
        self.lb_dsm_status.setText('已登陆')
        self.get_dsm_librarys()
        self.enabel_pages((1, 0, 0))

        self.show_finished = True

    # 窗口关闭后执行
    def closeEvent(self, event):
        super().closeEvent(event)
        self.config['dsm_search_keyword'] = self.edt_dsm_search_keyword.text()

        config = ConfigCache()
        config.save_cache(self.config, 'main_config')

        utils.add_log(self.logger, 'info', '保存配置文件：', 'closeEvent', self.config)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_form = MainForm()
    main_form.show()
    app.processEvents()
    main_form.form_showed()

    sys.exit(app.exec_())
