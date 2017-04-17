#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import imghdr
import logging
import sys
from time import sleep, time

import os
import requests
from PyQt5.QtCore import Qt, QSize, QByteArray, QBuffer, QIODevice
from PyQt5.QtGui import QPixmap, QIcon, QMovie, QPainter
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QListWidgetItem, QAbstractItemView, QListView, \
    QFileDialog, QMessageBox, QSplashScreen

import utils
from DSM.dsm_video_station import DSMAPI
from models.cache import DownCache
from models.http_server import HttpServer
from search_metadata_main import SearchMetadataDialog
from svm_login_main import LoginDialog
from ui.main_window import Ui_MainWindow


class MainForm(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)
        self.setupUi(self)

        self.db_config = DownCache(table_name='config')
        self.initUi()
        self.initListPices()

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

    def load_config(self):

        self.config = {}

        loadconfig = self.db_config.get_cache('main_config')

        if loadconfig:
            self.config.update(loadconfig)
        utils.add_log(self.logger, 'info', '读取配置文件：', self.config)

    def set_config(self):
        if self.config:
            self.edt_dsm_search_keyword.setText(self.config.get('dsm_search_keyword', ''))

    def initListPices(self):
        self.lst_pices.setIconSize(QSize(200, 200))
        self.lst_pices.setDragEnabled(True)
        self.lst_pices.setDragDropMode(QAbstractItemView.InternalMove)
        self.lst_pices.setMovement(QListView.Snap)
        self.lst_pices.setResizeMode(QListView.Adjust)
        self.lst_pices.setViewMode(QListView.ListMode)
        self.lst_pices.setFlow(QListView.LeftToRight)
        self.lst_pices.setWrapping(True)

        self.hs_zoom.setMaximum(200)
        self.hs_zoom.setProperty("value", 100)

        self.hs_zoom.valueChanged.connect(self.pic_zoom)
        self.btn_del_pic.clicked.connect(self.del_pic)
        self.btn_add_pic.clicked.connect(self.add_pic)

        self.tab_pices.setAcceptDrops(True)
        self.tab_pices.dragEnterEvent = self.tab_pices_dragEnterEvent
        self.tab_pices.dropEvent = self.tab_pices_dropEvent

    def initUi(self):
        self.tabWidget.setCurrentIndex(0)
        self.set_objects_enable('false')

        self.lb_dsm_status_cap = QLabel('DSM状态:')
        self.statusbar.addPermanentWidget(self.lb_dsm_status_cap)

        self.lb_dsm_status = QLabel('未登陆')
        self.statusbar.addPermanentWidget(self.lb_dsm_status)

        self.cb_dsm_search_kind.currentIndexChanged.connect(self.library_selected)

        self.btn_dsm_search.clicked.connect(lambda: self.btn_dsm_search_clicked(self.edt_dsm_search_keyword.text()))

        self.tbl_search_result_widget.put_meta.connect(self.select_dsm_video)

        self.cb_current_video.currentIndexChanged.connect(self.select_single_video)
        self.cb_current_video.currentIndexChanged[str].connect(self.status_msg)

        self.btn_fresh.clicked.connect(self.refresh_dsm)
        self.btn_save.clicked.connect(self.save_to_dsm)

        self.btn_meta_search.clicked.connect(self.search_metadata)

    def set_objects_enable(self, step):
        if step == 'false':
            self.cb_dsm_search_kind.setEnabled(False)
            self.edt_dsm_search_keyword.setEnabled(False)
            self.btn_dsm_search.setEnabled(False)

            self.tbl_search_result_widget.setEnabled(False)
            self.cb_current_video.setEnabled(False)
            self.btn_meta_search.setEnabled(False)
            self.btn_fresh.setEnabled(False)
            self.btn_save.setEnabled(False)
            self.btn_setting.setEnabled(False)

            self.tab_meta.setEnabled(False)
            self.tab_pices.setEnabled(False)

        if step == 'true':
            self.cb_dsm_search_kind.setEnabled(True)
            self.edt_dsm_search_keyword.setEnabled(True)
            self.btn_dsm_search.setEnabled(True)

            self.tbl_search_result_widget.setEnabled(True)
            self.cb_current_video.setEnabled(True)
            self.btn_meta_search.setEnabled(True)
            self.btn_fresh.setEnabled(True)
            self.btn_save.setEnabled(True)
            self.btn_setting.setEnabled(True)

            self.tab_meta.setEnabled(True)
            self.tab_pices.setEnabled(True)

        if step == 'after_list_libs' or step == 'seached':
            self.cb_dsm_search_kind.setEnabled(True)
            self.edt_dsm_search_keyword.setEnabled(True)
            self.btn_dsm_search.setEnabled(True)

            self.tbl_search_result_widget.setEnabled(False)
            self.cb_current_video.setEnabled(False)
            self.btn_meta_search.setEnabled(False)
            self.btn_fresh.setEnabled(False)
            self.btn_save.setEnabled(False)

            self.tab_meta.setEnabled(False)
            self.tab_pices.setEnabled(False)

            self.btn_setting.setEnabled(True)

        if step == 'searching':
            self.cb_dsm_search_kind.setEnabled(False)
            self.edt_dsm_search_keyword.setEnabled(False)
            self.btn_dsm_search.setEnabled(True)

            self.tbl_search_result_widget.setEnabled(False)
            self.cb_current_video.setEnabled(False)
            self.btn_meta_search.setEnabled(False)
            self.btn_fresh.setEnabled(False)
            self.btn_save.setEnabled(False)

            self.tab_meta.setEnabled(False)
            self.tab_pices.setEnabled(False)

        if step == 'seached':
            self.cb_dsm_search_kind.setEnabled(True)
            self.edt_dsm_search_keyword.setEnabled(True)
            self.btn_dsm_search.setEnabled(True)

            self.tbl_search_result_widget.setEnabled(True)
            self.cb_current_video.setEnabled(False)
            self.btn_meta_search.setEnabled(False)
            self.btn_fresh.setEnabled(False)
            self.btn_save.setEnabled(False)
            self.btn_setting.setEnabled(False)

            self.tab_meta.setEnabled(False)
            self.tab_pices.setEnabled(False)

    # 海报列表
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
        self.lst_pices.addItem(item)
        self.lst_pices.scrollToItem(item)

    def get_piclist_data_to_dict(self):
        for i in range(self.lst_pices.count()):
            try:
                item = self.lst_pices.item(i)
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

    def pic_zoom(self, value):
        size = 200 * value // 100
        self.lst_pices.setIconSize(QSize(size, size))

    # +按钮点击后添加图片
    def add_pic(self):
        fileName = QFileDialog.getOpenFileName(
            self, '选择图像文件', '', 'Images (*.jpg *.png *.gif *.bmp)')
        if fileName and os.path.isfile(fileName[0]):
            print(fileName[0])
            imgType = imghdr.what(fileName[0])
            print(imgType)
            if imgType:
                self.add_pic_fromData(fileName[0])
            else:
                QMessageBox.warning(self, '错误', '选择的文件无法读取！', QMessageBox.Ok)

    # -按钮 删除图片
    def del_pic(self):
        for item in self.lst_pices.selectedItems():
            self.lst_pices.takeItem(self.lst_pices.row(item))

    def tab_pices_dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def tab_pices_dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                imgType = imghdr.what(path)
                if imgType:
                    self.add_pic_fromData(path)
                else:
                    QMessageBox.warning(self, '错误', '选择的不是图像文件！', QMessageBox.Ok)

    def status_msg(self, msg):
        self.statusbar.showMessage(msg)

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

        self.cb_dsm_search_kind.addItem(QIcon(':/icons/ui_icons/all_video.png'), 'All', libs)

        for lib in libs:
            if lib.get('visible'):
                self.cb_dsm_search_kind.addItem(QIcon(':/icons/ui_icons/{}.png'.format(lib.get('type'))),
                                                lib.get('title'), lib)

        idx = min(self.cb_dsm_search_kind.count(), self.config.get('library_select_idx', 0))
        self.cb_dsm_search_kind.setCurrentIndex(idx)
        self.set_objects_enable('after_list_libs')

    def library_selected(self, idx):
        if self.show_finished:
            self.config['library_select_idx'] = idx

    # 搜索dsm
    def add_dsm_search_result(self, dsm_finded):
        if dsm_finded:
            try:
                self.tbl_search_result_widget.insert_data(dsm_finded)
            except Exception as e:
                utils.add_log(self.logger, 'error', 'add_dsm_search_result', e)

    def dsm_seach_videos(self, current_librarys, keyword):

        for current_library in current_librarys:
            if self.dsm_seach_stop:
                self.dsm_seach_running = False
                break
            yield current_library.get('title')

            for video in self.DSM.list_videos(current_library, keyword,self.chk_only_nil.checkState()):
                if self.dsm_seach_stop:
                    self.dsm_seach_running = False
                    break

                yield video

    def btn_dsm_search_clicked(self, keyword):
        if self.dsm_seach_running:
            self.dsm_seach_stop = True
            self.set_objects_enable('seached')
        else:
            if self.cb_dsm_search_kind.currentIndex() == 0:
                current_librarys = self.cb_dsm_search_kind.currentData(Qt.UserRole)

            else:
                current_librarys = [self.cb_dsm_search_kind.currentData(Qt.UserRole)]

            self.dsm_seach_stop = False
            self.dsm_seach_running = True
            self.tbl_search_result_widget.clear_data()
            self.set_objects_enable('searching')
            start_time = time()
            try:

                total = 0
                count = 0

                current_library_title = ''

                for video in self.dsm_seach_videos(current_librarys, keyword):
                    try:
                        if self.dsm_seach_stop:
                            break
                        if isinstance(video, int):
                            total += video
                            continue
                        if isinstance(video, str):
                            current_library_title = video
                            continue
                        count += 1
                        self.add_dsm_search_result(video)
                    finally:
                        self.status_msg(
                            '[VideoStation搜索:{}]找到[{}/{}]个,耗时:{}'.format(current_library_title, count, total,
                                                                         utils.seconds_to_struct(time() - start_time)))
                        app.processEvents()
                    app.processEvents()
                self.status_msg('[VideoStation搜索]完成！共找到[{}/{}]个,耗时:{},双击选择影片进一步处理'.format(count, total,
                                                                                          utils.seconds_to_struct(
                                                                                              time() - start_time)))

            except Exception as e:
                utils.add_log(self.logger, 'error', 'btn_dsm_search_clicked', e.args)
            finally:
                self.dsm_seach_running = False
                self.btn_dsm_search.setChecked(False)
                self.set_objects_enable('seached')

    #####选择视频
    def add_cb_current_videoitems(self, videos,stype= ''):
        if not videos:
            return
        for video in videos:
            if not stype:
                stype = video.get('tag').get('type')
            else:
                video['tag']['type'] = stype
            if not stype:
                return
            title = video.get('标题')
            if not title:
                title = video.get('电视节目标题')
            if not title:
                return

            file_name = video.get('文件名')

            if not file_name:
                if stype == 'tvshow_episode':
                    file_name = '{}.S{}.E{}.{}'.format(title,
                                                       video.get('季').zfill(2),
                                                       video.get('集').zfill(2),
                                                       video.get('集标题'))
                else:
                    file_name = title

            self.cb_current_video.addItem(QIcon(':/icons/ui_icons/{}.png'.format(stype)), file_name, video)
        # if not videos:
        #     return
        # for video in videos:
        #
        #     meta_cb = {
        #         'type': stype,
        #         'id': video.get('id'),
        #         'library_id': video.get('library_id'),
        #         'mapper_id': video.get('mapper_id'),
        #         'title': video.get('title'),
        #         'path': '',
        #         'sharepath': '',
        #     }
        #     file_data = video.get('additional').get('file')
        #     if file_data:
        #         meta_cb.update({
        #             'path': video.get('additional').get('file')[0].get('path'),
        #             'sharepath': video.get('additional').get('file')[0].get('sharepath'),
        #         })
        #     file_name = os.path.basename(meta_cb.get('path'))
        #     if not file_name:
        #         if stype == 'tvshow_episode':
        #             file_name = '{}.S{}.E{}.{}'.format(video.get('title'),
        #                                                str(video.get('season')).zfill(2),
        #                                                str(video.get('episode')).zfill(2),
        #                                                video.get('tagline'))
        #         else:
        #             file_name = meta_cb.get('title')
        #
        #     self.cb_current_video.addItem(QIcon(':/icons/ui_icons/{}.png'.format(stype)), file_name, meta_cb)

    # 鼠标选中视频
    def select_dsm_video(self, meta):
        if meta:
            self.set_objects_enable('false')
            self.repaint()
            app.processEvents()
            try:
                self.cb_current_video_add_finish = False
                self.cb_current_video.clear()

                # stype = meta.get('tag').get('type')
                videos = self.DSM.get_video_info(meta)
                self.add_cb_current_videoitems(videos)
                app.processEvents()
                if  meta.get('tag').get('type') == 'tvshow':
                    episodes = self.DSM.get_video_info(meta,'tvshow_episode')
                    self.add_cb_current_videoitems(episodes,'tvshow_episode')
                    app.processEvents()

                # stype = meta.get('type')
                # sid = meta.get('id')
                # slibrary_id = meta.get('library_id')
                #
                # videos = self.DSM.get_video_info(sid, stype, slibrary_id)
                # self.add_cb_current_videoitems(videos, stype)
                # app.processEvents()
                # if stype == 'tvshow':
                #     episodes = self.DSM.get_video_info(sid, 'tvshow_episode', slibrary_id)
                #     self.add_cb_current_videoitems(episodes, 'tvshow_episode')
                #     app.processEvents()

            finally:
                self.cb_current_video_add_finish = True
                self.select_single_video(0)
                self.tabWidget.setCurrentIndex(0)
                self.set_objects_enable('true')

    def select_single_video(self, idx):
        try:
            if self.cb_current_video_add_finish:
                video = self.cb_current_video.currentData(Qt.UserRole)
                if video:
                    self.status_msg('[VideoStation]正在读取……')
                    video_dital = self.DSM.get_video_dital_info(video)
                    self.table_video_meta.ref_table(video_dital)
                    self.lst_pices.clear()
                    if video_dital.get('tag').get('poster'):
                        self.add_pic_fromData(video_dital.get('tag').get('poster'))
                    if video_dital.get('tag').get('backdrop'):
                        self.add_pic_fromData(video_dital.get('tag').get('backdrop'))
        finally:
            self.status_msg('[VideoStation]读取完成')

        # try:
        #     if self.cb_current_video_add_finish:
        #         video = self.cb_current_video.currentData(Qt.UserRole)
        #         if video:
        #             self.status_msg('[VideoStation]正在读取……')
        #             video_dital = self.DSM.get_video_dital_info(video.get('id'), video.get('type'))
        #             self.table_video_meta.ref_table(video_dital)
        #             self.lst_pices.clear()
        #             if video_dital.get('poster'):
        #                 self.add_pic_fromData(video_dital.get('poster'))
        #             if video_dital.get('backdrop'):
        #                 self.add_pic_fromData(video_dital.get('backdrop'))
        # finally:
        #     self.status_msg('[VideoStation]读取完成')

    def refresh_dsm(self):
        self.set_objects_enable('false')
        self.select_single_video(0)
        self.set_objects_enable('true')

    def save_to_dsm(self):
        self.set_objects_enable('false')
        app.processEvents() #todo 摘要截断 ﻿Pirates II: Stagnetti's Revenge
        try:
            meta = self.table_video_meta.get_metadata(self.cb_current_video.currentData(Qt.UserRole))
            meta['tag']['poster']=b''
            meta['tag']['backdrop'] = b''
            for i, img_data in enumerate(self.get_piclist_data_to_dict()):
                app.processEvents()
                if not img_data:
                    break
                if i == 0:
                    meta['tag']['poster'] = img_data
                elif i == 1:
                    meta['tag']['backdrop'] = img_data
                else:
                    break

            tag = meta.get('tag')

            if tag.get('poster'):
                self.DSM.set_poster(tag.get('type'), tag.get('id'), tag.get('poster'))
                self.status_msg('[VideoStation]写入封面海报……')
                app.processEvents()
            else:
                self.DSM.del_poster(tag.get('type'), tag.get('id'))

            if tag.get('backdrop'):
                self.DSM.set_backdrop(tag.get('type'), tag.get('id'), tag.get('backdrop'))
                self.status_msg('[VideoStation]写入背景海报……')
                app.processEvents()
            else:
                self.DSM.del_backdrop(tag.get('type'), tag.get('id'), tag.get('mapper_id'))

            self.status_msg('[VideoStation]写入元数据……')
            app.processEvents()
            if not self.DSM.set_video_info(meta):
                QMessageBox.warning(self, '错误', '写入元数据失败！', QMessageBox.Ok)
                return

            self.select_single_video(0)
            # 回写搜索结果
            row = self.tbl_search_result_widget.currentRow()
            # data = self.table_video_meta.get_metadata(self.cb_current_video.currentData(Qt.UserRole))
            # data.update({
            #     'poster': b'',
            #     'backdrop': b'',
            # })
            # for i, img_data in enumerate(self.get_piclist_data_to_dict()):
            #     app.processEvents()
            #     if not img_data:
            #         break
            #     if i == 0:
            #         data['tag']['poster'] = img_data
            #     elif i == 1:
            #         data['tag']['backdrop'] = img_data
            #     else:
            #         break
            self.tbl_search_result_widget.insert_data(meta, row)

            app.processEvents()
        finally:
            self.set_objects_enable('true')

    # 窗口显示后执行
    def form_showed(self):
        utils.add_log(self.logger, 'info', '检测是否登陆dsm')
        self.check_login_status()
        self.lb_dsm_status.setText('已登陆')
        self.get_dsm_librarys()
        self.HttpServer = HttpServer(utils.HTTP_SERVER_PORT)

        self.show_finished = True

    # 窗口关闭后执行
    def closeEvent(self, event):
        super().closeEvent(event)
        if self.dsm_seach_running:
            event.ignore()
            QMessageBox.warning(self, '错误', '请先停止搜索再尝试关闭！', QMessageBox.Ok)
            return
        self.config['dsm_search_keyword'] = self.edt_dsm_search_keyword.text()

        self.db_config.save_cache('main_config', self.config, 0, 0)

        utils.add_log(self.logger, 'info', '保存配置文件：', 'closeEvent', self.config)

    # 搜索元数据
    def search_metadata(self):
        self.search_meta_form = SearchMetadataDialog()
        meta = self.table_video_meta.get_metadata(self.cb_current_video.currentData(Qt.UserRole))
        if meta:
            self.search_meta_form.open_dialog(meta)
            self.search_meta_form.exec_()
            if self.search_meta_form:
                self.table_video_meta.modifiy_table(self.search_meta_form.meta_return)
            if self.search_meta_form.pices_return:
                for pic_data in self.search_meta_form.pices_return:
                    self.add_pic_fromData(pic_data)

            self.btn_meta_search.setChecked(False)


class MovieSplashScreen(QSplashScreen):
    def __init__(self, movie, parent=None):
        movie.jumpToFrame(0)
        pixmap = QPixmap(movie.frameRect().size())

        QSplashScreen.__init__(self, pixmap)
        self.movie = movie
        self.movie.frameChanged.connect(self.repaint)

    def showEvent(self, event):
        self.movie.start()

    def hideEvent(self, event):
        self.movie.stop()

    def paintEvent(self, event):
        painter = QPainter(self)
        pixmap = self.movie.currentPixmap()
        self.setMask(pixmap.mask())
        painter.drawPixmap(0, 0, pixmap)

    def sizeHint(self):
        return self.movie.scaledSize()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # movie = QMovie(":/icons/others/span.gif")
    # splash = MovieSplashScreen(movie)
    # splash.show()
    # app.processEvents()
    # start = time()
    # while movie.state() == QMovie.Running and time() < start + 3:
    #     app.processEvents()

    splash = QSplashScreen(QPixmap(":/icons/others/span.gif"))
    splash.show()

    app.processEvents()
    DownCache.del_expire()
    main_form = MainForm()
    main_form.show()
    # app.processEvents()
    main_form.form_showed()

    splash.finish(main_form)

    sys.exit(app.exec_())
