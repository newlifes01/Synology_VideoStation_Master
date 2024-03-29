#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import socket

import os
import requests
from PyQt5.QtCore import QThread

import utils
from dsm_merge_main import DSMMerge
from models.cache import DownCache


class DSMAPI(QThread):
    def __init__(self, session, ip):
        super().__init__()
        self.logger = logging.getLogger('DSMAPI')
        self.ip = ip
        self.session = session
        self.cache = DownCache(table_name='dsm_cache')
        self.set_cookie_form_cache()

    def add_log(self, *msg, level='info'):
        utils.add_log(self.logger, level, msg)

    def __load_cookie(self):
        login_data = self.cache.get_cache('cookie')

        if login_data:
            cookies = login_data.get('cookies')
            ip = login_data.get('ip')
            return ip, cookies
        return '', {}

    def __save_cookie(self):
        cookies = {
            'cookies': requests.utils.dict_from_cookiejar(self.session.cookies),
            'ip': self.ip
        }
        self.cache.save_cache('cookie', cookies, 0, 0)

    def post_request(self, cgi, api='', method='', extra=None, bytes=False, cache=False):
        if not self.ip:
            return None
        try:
            data = {
                'api': api,
                'method': method,
                'version': '1',
            }
            if extra:
                data.update(extra)

            res = self.session.post('http://{}/webapi/{}'.format(self.ip, cgi), data=data)

            if res.status_code == 200:
                if bytes:
                    return res.content
                else:
                    return res.json()
        except Exception as e:
            self.add_log('post_request', e,level='error')
            return None

    def set_cookie_form_cache(self):
        ip, cookies = self.__load_cookie()
        if not cookies or not ip:
            return False
        else:
            self.ip = ip
            requests.utils.add_dict_to_cookiejar(self.session.cookies, cookies)
            self.add_log('设置登陆信息', ip, cookies)

    def check_login_status(self):
        if not self.ip:
            return False
        url = 'http://{}/{}'.format(self.ip, 'webman/login.cgi?enable_syno_token=yes')
        res = self.session.post(url)
        if res.status_code == 200:
            json_res = res.json()
            if json_res and json_res.get('success'):
                self.__save_cookie()

                self.add_log('保存登陆信息')
                return True
        return False

    def login_dsm(self, account, password):
        if not account or not password:
            return False
        json_res = self.post_request('auth.cgi', 'SYNO.API.Auth', 'login', {'account': account, 'passwd': password})
        if json_res and json_res.get('success'):
            self.__save_cookie()
            return True

    def get_librarys(self):
        json_res = self.post_request('entry.cgi', 'SYNO.VideoStation2.Library', 'list')
        if json_res and json_res.get('success'):
            liblist = json_res.get('data').get('library')
            return liblist

    def get_video_poster(self, stype, id, mtime):

        if not mtime:
            return

        cache_name = 'poster-{}-{}'.format(stype, id)

        bytes_res = self.cache.get_cache(cache_name, utils.format_time_stamp(mtime))
        if not bytes_res:
            param = {
                'type': '{}'.format(stype),
                'id': '{}'.format(id),
            }
            bytes_res = self.post_request('entry.cgi', 'SYNO.VideoStation2.Poster', 'get', param, bytes=True)
            if bytes_res:
                self.cache.save_cache(cache_name, bytes_res, utils.format_time_stamp(mtime), 0)
        return bytes_res

    def get_video_backdrop(self, mapper_id, mtime):
        if not mtime:
            return

        cache_name = 'backdrop-{}'.format(mapper_id)

        bytes_res = self.cache.get_cache(cache_name, utils.format_time_stamp(mtime))
        if not bytes_res:
            param = {
                'mapper_id': '{}'.format(mapper_id),
            }
            bytes_res = self.post_request('entry.cgi', 'SYNO.VideoStation2.Backdrop', 'get', param, bytes=True)
            if bytes_res:
                self.cache.save_cache(cache_name, bytes_res, utils.format_time_stamp(mtime), 0)

        return bytes_res

    # 列出指定资料库所有影片
    def list_videos(self, meta, keyword='', only_nil=False):
        if not meta:
            return
        stype = meta.get('type')
        sAPI = utils.get_library_API(stype)
        library_id = meta.get('id')
        heads = utils.get_dsm_json_head(stype)

        if library_id is None or not sAPI:
            return

        param = {
            'offset': '0',
            'limit': '5000',
            'sort_by': '"title"',
            'sort_direction': '"desc"',
            'library_id': '{}'.format(library_id),
            'additional': '["poster_mtime","backdrop_mtime","summary"]'
        }

        if keyword:
            param.update({'keyword': '"{}"'.format(keyword)})

        json_res = self.post_request('entry.cgi', 'SYNO.VideoStation2.{}'.format(sAPI), 'list', param)
        if json_res and json_res.get('success'):

            total = json_res.get('data').get('total')
            if total:
                yield total

            datas = json_res.get('data').get(heads)

            for data in datas:

                test_meta = utils.gen_metadata_struck(stype)
                if test_meta:
                    result_data = utils.fill_cn_form_en(stype, test_meta, data)
                    if result_data:
                        poster_mtime = data.get('additional').get('poster_mtime')
                        poster = self.get_video_poster(stype, data.get('id'), poster_mtime)
                        result_data['tag']['poster'] = poster
                        if only_nil:
                            if not result_data.get('tag').get('poster_mtime'):
                                yield result_data
                        else:
                            yield result_data

    def get_video_info(self, meta, stype=''):
        if not meta:
            return
        if not stype:
            stype = meta.get('tag').get('type')

        if not stype:
            return

        sid = meta.get('tag').get('id')
        slibrary_id = meta.get('tag').get('library_id')

        param = {
            'id': '[{}]'.format(sid),
        }
        if stype == 'tvshow':
            param.update({'additional': '["poster_mtime","summary","backdrop_mtime"]'})

        if stype == 'movie' or stype == 'home_video':
            param.update({
                'additional': '["summary","poster_mtime","backdrop_mtime","file","collection","watched_ratio","conversion_produced","actor","director","genre","writer","extra"]'
            })

        if stype == 'tvshow_episode':
            param = {
                'library_id': '{}'.format(slibrary_id),
                'tvshow_id': '{}'.format(sid),
                'limit': '500000',
                'additional': '["summary","collection","poster_mtime","watched_ratio","file"]',
            }

        meth = 'getinfo'
        if stype == 'tvshow_episode':
            meth = 'list'

        json_res = self.post_request('entry.cgi', 'SYNO.VideoStation2.{}'.format(utils.get_library_API(stype)),
                                     meth, param)
        if json_res:
            results = json_res.get('data').get(utils.get_dsm_json_head(stype))
            for result in results:
                test_meta = utils.gen_metadata_struck(stype)
                if test_meta:
                    result_data = utils.fill_cn_form_en(stype, test_meta, result)
                    yield result_data

    def get_video_dital_info(self, video):
        sid = video.get('tag').get('id')
        stype = video.get('tag').get('type')
        param = {
            'id': '[{}]'.format(sid),
        }
        if stype == 'tvshow':
            param.update({'additional': '["poster_mtime","summary","backdrop_mtime"]'})

        if stype == 'tvshow_episode':
            param.update({
                'additional': '["summary","poster_mtime","backdrop_mtime","file","collection","watched_ratio","conversion_produced","actor","director","genre","writer","extra","tvshow_summary"]'})

        if stype == 'movie' or stype == 'home_video':
            param.update({
                'additional': '["summary","poster_mtime","backdrop_mtime","file","collection","watched_ratio","conversion_produced","actor","director","genre","writer","extra"]'})

        json_res = self.post_request('entry.cgi', 'SYNO.VideoStation2.{}'.format(utils.get_library_API(stype)),
                                     'getinfo', param)

        if json_res:
            head = utils.get_dsm_json_head(stype)
            meta = json_res.get('data').get(head)[0]
            video_meta = utils.fill_cn_form_en(stype, video, meta)
            poster = self.get_video_poster(stype, sid, meta.get('additional').get('poster_mtime'))
            if poster:
                video_meta['tag']['poster'] = poster
            backdrop = self.get_video_backdrop(video.get('tag').get('mapper_id'),
                                               meta.get('additional').get('backdrop_mtime'))
            if backdrop:
                video_meta['tag']['backdrop'] = backdrop
            return video_meta

    # 删除封面:
    def del_poster(self, stype, sid):
        if not stype or not sid:
            return
        param = {
            'id': '{}'.format(sid),
            'type': '"{}"'.format(stype),
        }
        json_res = self.post_request('entry.cgi', 'SYNO.VideoStation2.Poster', 'delete', param)
        return json_res and json_res.get('success')

    # 删除背景
    def del_backdrop(self, stype, sid, mapper_id):
        if not stype or not sid:
            return
        param = {

            'id': '{}'.format(sid),
            'type': '"{}"'.format(stype),
            'image': '"clear"',
            'keep_one': 'true',
            'mapper_id': '{}'.format(mapper_id),
        }
        json_res = self.post_request('entry.cgi', 'SYNO.VideoStation2.Backdrop', 'delete_all', param)
        return json_res and json_res.get('success')

    # 设置封面
    def set_poster(self, stype, sid, image_data):
        if not stype or not sid or not image_data:
            return

        if os.path.isfile(utils.POSTER_PATH):
            os.remove(utils.POSTER_PATH)

        if image_data:
            self.add_log('创建临时封面:', utils.POSTER_PATH)
            with open(utils.POSTER_PATH, 'wb') as f:
                f.write(image_data)

        if os.path.isfile(utils.POSTER_PATH):
            myname = socket.getfqdn(socket.gethostname())
            addr = socket.gethostbyname(myname)
            param = {
                'id': '{}'.format(sid),
                'type': '"{}"'.format(stype),
                'target': '"url"',
                'url': '"http://{}:{}/{}"'.format(addr, utils.HTTP_SERVER_PORT,
                                                  utils.POSTER_FILE),
            }
            json_res = self.post_request('entry.cgi', 'SYNO.VideoStation2.Poster', 'set', param)
            if os.path.isfile(utils.POSTER_PATH):
                self.add_log('删除临时封面:', utils.POSTER_PATH)
                os.remove(utils.POSTER_PATH)
            return json_res and json_res.get('success')

    # 设置背景图
    def set_backdrop(self, stype, sid, image_data):
        if not stype or not sid or not image_data:
            return

        if os.path.isfile(utils.BACKDROP_PATH):
            os.remove(utils.BACKDROP_PATH)

        if image_data:
            self.add_log('创建临时背景:', utils.BACKDROP_PATH)
            with open(utils.BACKDROP_PATH, 'wb') as f:
                f.write(image_data)

        if os.path.isfile(utils.BACKDROP_PATH):
            myname = socket.getfqdn(socket.gethostname())
            addr = socket.gethostbyname(myname)
            data = {
                'id': '{}'.format(sid),
                'type': '"{}"'.format(stype),
                'target': '"url"',
                'url': '"http://{}:{}/{}"'.format(addr, utils.HTTP_SERVER_PORT,
                                                  utils.BACKDROP_FILE),
                'keep_one': 'true',
            }
            json_res = self.post_request('entry.cgi', 'SYNO.VideoStation2.Backdrop', 'add', data)
            if os.path.isfile(utils.BACKDROP_PATH):
                self.add_log('删除临时背景:', utils.BACKDROP_PATH)
                os.remove(utils.BACKDROP_PATH)
            return json_res.get('success')

    def set_video_info(self, meta,merge_meth=''):
        if not meta:
            return
        stype = meta.get('tag').get('type')
        if not stype:
            return
        param = None

        if stype == 'home_video':
            param = {
                'library_id': '{}'.format(meta.get('tag').get('library_id')),
                'target': '"video"',
                'id': '{}'.format(meta.get('tag').get('id')),
                'title': '"{}"'.format(meta.get('标题', '')),

                'record_date_date': '"{}"'.format(utils.format_date_str(meta.get('录制开始时间', ''))),
                'record_date_time': '"{}"'.format(utils.format_time_str(meta.get('录制开始时间', ''))),
                'certificate': '"{}"'.format(meta.get('级别', '')),
                'rating': '{}'.format(meta.get('评级', '')),
                'genre': utils.gen_liststr(meta.get('类型', '')),
                'actor': utils.gen_liststr(meta.get('演员', '')),
                'writer': utils.gen_liststr(meta.get('作者', '')),
                'director': utils.gen_liststr(meta.get('导演', '')),
                'metadata_locked': 'true',
                'summary': '"{}"'.format(meta.get('摘要', '')),
                'record_date': '"{}"'.format(utils.format_date_time_str(meta.get('录制开始时间', ''))),

            }

        if stype == 'tvshow':
            param = {
                'library_id': '{}'.format(meta.get('tag').get('library_id')),
                'target': '"video"',
                'id': '{}'.format(meta.get('tag').get('id')),
                'title': '"{}"'.format(meta.get('电视节目标题', '')),
                'original_available': '"{}"'.format(utils.format_date_str(meta.get('发布日期', ''))),
                'metadata_locked': 'true',
                'summary': '"{}"'.format(meta.get('摘要', '')),
                'extra': '"null"',
                'update_tvshow': '""',
            }

        if stype == 'tvshow_episode':
            param = {
                'library_id': '{}'.format(meta.get('tag').get('library_id')),
                'target': '"video"',
                'id': '{}'.format(meta.get('tag').get('id')),
                'title': '"{}"'.format(meta.get('电视节目标题', '')),
                'tvshow_original_available': '"{}"'.format(utils.format_date_str(meta.get('发布日期(电视节目)', ''))),
                'tagline': '"{}"'.format(meta.get('集标题', '')),
                'season': '{}'.format(meta.get('季', '')),
                'episode': '{}'.format(meta.get('集', '')),
                'original_available': '"{}"'.format(utils.format_date_str(meta.get('发布日期(集)', ''))),
                'certificate': '"{}"'.format(meta.get('级别', '')),
                'rating': '{}'.format(meta.get('评级', '')),
                'genre': utils.gen_liststr(meta.get('类型', '')),
                'actor': utils.gen_liststr(meta.get('演员', '')),
                'writer': utils.gen_liststr(meta.get('作者', '')),
                'director': utils.gen_liststr(meta.get('导演', '')),
                'metadata_locked': 'true',
                'summary': '"{}"'.format(meta.get('摘要', '')),
                'extra': '"null"',
                'tvshow_extra': '"null"',
            }
        if stype == 'movie':
            param = {
                'library_id': '{}'.format(meta.get('tag').get('library_id')),
                'target': '"video"',
                'id': '{}'.format(meta.get('tag').get('id')),
                'title': '"{}"'.format(meta.get('标题', '')),
                'tagline': '"{}"'.format(meta.get('标语', '')),
                'original_available': '"{}"'.format(utils.format_date_str(meta.get('发布日期', ''))),
                'certificate': '"{}"'.format(meta.get('级别', '')),
                'rating': '{}'.format(meta.get('评级', '')),
                'genre': utils.gen_liststr(meta.get('类型', '')),
                'actor': utils.gen_liststr(meta.get('演员', '')),
                'writer': utils.gen_liststr(meta.get('作者', '')),
                'director': utils.gen_liststr(meta.get('导演', '')),
                'metadata_locked': 'true',
                'summary': '"{}"'.format(meta.get('摘要', '')),
                'extra': '"null"',
            }
        if not param:
            return
        if merge_meth:
            param['overwrite'] = merge_meth
        json_res = self.post_request('entry.cgi', 'SYNO.VideoStation2.{}'.format(utils.get_library_API(stype)), 'edit',
                                     param)
        if json_res:
            if json_res.get('error'):
                if json_res.get('error').get('code') == 600:
                    meth = ''
                    dsm_merge = DSMMerge()
                    if dsm_merge.exec_():
                        meth = dsm_merge.meth

                        if meth:
                            self.add_log('存在相同视频,处理方式：',meth)
                            return self.set_video_info(meta,meth),True

                    self.add_log('存在相同视频,处理方式：', '放弃')
                    return True,False

        return json_res.get('success'),False


if __name__ == '__main__':
    session = requests.session()
    # requests.utils.add_dict_to_cookiejar(session.cookies, {
    #     'stay_login': '1',
    #     'id': 'ez6HTNdVuGbhs1610NEN304901'
    # })

    dsm = DSMAPI(session, '192.168.2.97:5000')

    while not dsm.check_login_status():
        if dsm.login_dsm('syaofox', '090109'):
            print('已登陆')
