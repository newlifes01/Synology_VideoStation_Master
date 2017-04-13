#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import socket
from datetime import datetime

import os
import requests
from PyQt5.QtCore import QThread

import utils
from models.cache import ConfigCache, DownCache


class DSMAPI(QThread):
    def __init__(self, session, ip):
        super().__init__()
        self.logger = logging.getLogger('DSMAPI')
        self.ip = ip
        self.session = session
        self.config = ConfigCache()
        self.set_cookie_form_cache()
        self.cache = DownCache()

    def format_time(self, timestr):
        return datetime.strptime(timestr, '%Y-%m-%d %H:%M:%S.%f')

    def __load_cookie(self):
        login_data = self.config.get_cache('cookies')
        if login_data:
            cookies = login_data.get('cookies')
            ip = login_data.get('ip')
            return ip, cookies
        return '', {}

    def __save_cookie(self):
        self.config.save_cache({
            'cookies': requests.utils.dict_from_cookiejar(self.session.cookies),
            'ip': self.ip
        }, 'cookies')

    def post_request(self, cgi, api='', method='', extra=None, bytes=False):
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
            utils.add_log(self.logger, 'error', 'post_request', e)
            return None

    def set_cookie_form_cache(self):
        ip, cookies = self.__load_cookie()
        if not cookies or not ip:
            return False
        else:
            self.ip = ip
            requests.utils.add_dict_to_cookiejar(self.session.cookies, cookies)
            utils.add_log(self.logger, 'info', '设置登陆信息', ip, cookies)

    def check_login_status(self):
        if not self.ip:
            return False
        url = 'http://{}/{}'.format(self.ip, 'webman/login.cgi?enable_syno_token=yes')
        res = self.session.post(url)
        if res.status_code == 200:
            json_res = res.json()
            if json_res and json_res.get('success'):
                self.__save_cookie()

                utils.add_log(self.logger, 'info', '保存登陆信息')
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
            mtime = '2000-01-01 00:00:00.000000'

        # cache_name = '{}-{}-{}'.format(stype, id, mtime)
        cache_name = '{}-{}'.format(stype, id)

        bytes_res = self.cache.get_cache(cache_name, self.format_time(mtime), utils.IMG_CACHE_SUBDIR)
        if not bytes_res:
            param = {
                'type': '{}'.format(stype),  # movie
                'id': '{}'.format(id),
            }
            bytes_res = self.post_request('entry.cgi', 'SYNO.VideoStation2.Poster', 'get', param, bytes=True)
            if bytes_res:
                self.cache.save_cache(cache_name, bytes_res, self.format_time(mtime), utils.IMG_CACHE_SUBDIR)
        return bytes_res

    def get_video_backdrop(self, mapper_id, mtime):  # todo 不是所有类型都有背景图
        if not mtime:
            return

        # cache_name = '{}-{}'.format(mapper_id, mtime)
        cache_name = '{}'.format(mapper_id)

        bytes_res = self.cache.get_cache(cache_name, self.format_time(mtime), utils.IMG_CACHE_SUBDIR)
        if not bytes_res:
            param = {
                'mapper_id': '{}'.format(mapper_id),
            }
            bytes_res = self.post_request('entry.cgi', 'SYNO.VideoStation2.Backdrop', 'get', param, bytes=True)
            if bytes_res:
                self.cache.save_cache(cache_name, bytes_res, self.format_time(mtime), utils.IMG_CACHE_SUBDIR)

        return bytes_res

    # 列出指定资料库所有影片
    def list_videos(self, meta, keyword=''):
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
            'sort_by': '"title"',  # added
            'sort_direction': '"desc"',
            'library_id': '{}'.format(library_id),
            'additional': '["poster_mtime","backdrop_mtime"]'
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
                result_data = {}

                poster_mtime = data.get('additional').get('poster_mtime')

                poster = self.get_video_poster(stype, data.get('id'), poster_mtime)

                backdrop_mtime = data.get('additional').get('backdrop_mtime')

                backdrop = self.get_video_backdrop(data.get('mapper_id'), backdrop_mtime)

                result_data.update({
                    'type': stype,
                    'API': sAPI,
                    'json_head': heads,

                    'title': data.get('title'),

                    'id': data.get('id'),
                    'library_id': data.get('library_id'),
                    'mapper_id': data.get('mapper_id'),

                    'poster_mtime': poster_mtime,
                    'backdrop_mtime': backdrop_mtime,
                    'poster': poster,
                    'backdrop': backdrop,
                    'total_seasons': data.get('additional').get('total_seasons', 0),
                    'original_available': utils.format_date_str(data.get('original_available', '')),
                    'record_date': utils.format_date_str(data.get('record_date', '')),

                })

                yield result_data

    def get_video_info(self, id, stype, library_id):
        if not id or not stype:
            return

        param = {
            'id': '[{}]'.format(id),
        }
        if stype == 'tvshow':
            param.update({'additional': '["poster_mtime","summary","backdrop_mtime"]'})

        if stype == 'movie' or stype == 'home_video':
            param.update({
                'additional': '["summary","poster_mtime","backdrop_mtime","file","collection","watched_ratio","conversion_produced","actor","director","genre","writer","extra"]'
            })

        if stype == 'tvshow_episode':
            param = {
                'library_id': '{}'.format(library_id),
                'tvshow_id': '{}'.format(id),
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
            # if stype == 'home_video':
            #     results = json_res.get('data').get('video')
            # elif stype == 'tvshow_episode':
            #     results = json_res.get('data').get('episode')
            # else:
            #     results = json_res.get('data').get(stype)
            for result in results:
                yield result

    def get_video_dital_info(self, sid, stype):
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
            video_meta = None
            if stype == 'tvshow_episode':
                meta = json_res.get('data').get('episode')[0]
                video_meta = utils.get_dital_episode_struck()
                poster = self.get_video_poster(stype, meta.get('id'),
                                               meta.get('additional').get('poster_mtime'))
                video_meta['poster'] = poster

                video_meta['文件名'] = os.path.basename(meta.get('additional').get('file')[0].get('sharepath'))

                video_meta['电视节目标题'] = meta.get('title', '')
                video_meta['发布日期(电视节目)'] = utils.format_date_str(meta.get('tvshow_original_available', ''))
                video_meta['集标题'] = meta.get('tagline', '')
                video_meta['季'] = str(meta.get('season', 0))
                video_meta['集'] = str(meta.get('episode', 0))
                video_meta['发布日期(集)'] = utils.format_date_str(meta.get('original_available', ''))
                video_meta['级别'] = meta.get('certificate', '')
                video_meta['评级'] = str(meta.get('rating', 0))
                video_meta['类型'] = ','.join(meta.get('additional').get('genre', []))
                video_meta['演员'] = ','.join(meta.get('additional').get('actor', []))
                video_meta['作者'] = ','.join(meta.get('additional').get('writer', []))
                video_meta['导演'] = ','.join(meta.get('additional').get('director', []))
                video_meta['摘要'] = meta.get('additional').get('summary', '')

            if stype == 'tvshow':
                meta = json_res.get('data').get(stype)[0]
                video_meta = utils.get_dital_tvshow_struck()
                poster = self.get_video_poster(stype, meta.get('id'),
                                               meta.get('additional').get('poster_mtime'))
                video_meta['poster'] = poster

                backdrop = self.get_video_backdrop(meta.get('mapper_id'),
                                                   meta.get('additional').get('backdrop_mtime'))
                video_meta['backdrop'] = backdrop

                video_meta['电视节目标题'] = meta.get('title', '')
                video_meta['发布日期'] = utils.format_date_str(meta.get('original_available', ''))

                video_meta['摘要'] = meta.get('additional').get('summary', '')
                video_meta['季数'] = str(meta.get('additional').get('total_seasons', 0))

            if stype == 'movie':
                meta = json_res.get('data').get(stype)[0]
                video_meta = utils.get_dital_movie_struck()
                poster = self.get_video_poster(stype, meta.get('id'),
                                               meta.get('additional').get('poster_mtime'))
                video_meta['poster'] = poster

                backdrop = self.get_video_backdrop(meta.get('mapper_id'),
                                                   meta.get('additional').get('backdrop_mtime'))
                video_meta['backdrop'] = backdrop

                video_meta['文件名'] = os.path.basename(meta.get('additional').get('file')[0].get('sharepath'))

                video_meta['标题'] = meta.get('title', '')
                video_meta['标语'] = meta.get('tagline', '')

                video_meta['发布日期'] = utils.format_date_str(meta.get('original_available', ''))
                video_meta['级别'] = meta.get('certificate', '')
                video_meta['评级'] = str(meta.get('rating', 0))
                video_meta['类型'] = ','.join(meta.get('additional').get('genre', []))
                video_meta['演员'] = ','.join(meta.get('additional').get('actor', []))
                video_meta['作者'] = ','.join(meta.get('additional').get('writer', []))
                video_meta['导演'] = ','.join(meta.get('additional').get('director', []))
                video_meta['摘要'] = meta.get('additional').get('summary', '')

            if stype == 'home_video':
                meta = json_res.get('data').get('video')[0]
                video_meta = utils.get_dital_homevideo_struck()
                poster = self.get_video_poster(stype, meta.get('id'),
                                               meta.get('additional').get('poster_mtime'))
                video_meta['poster'] = poster

                video_meta['文件名'] = os.path.basename(meta.get('additional').get('file')[0].get('sharepath'))

                video_meta['标题'] = meta.get('title', '')

                video_meta['录制开始时间'] = utils.format_date_time_str(meta.get('record_date', ''))
                # video_meta['录制开始时间'] = utils.format_date_str(meta.get('record_date', ''))
                # video_meta['时间'] = utils.format_time_str(meta.get('record_date', ''))
                video_meta['级别'] = meta.get('certificate', '')
                video_meta['评级'] = str(meta.get('rating', 0))
                video_meta['类型'] = ','.join(meta.get('additional').get('genre', []))
                video_meta['演员'] = ','.join(meta.get('additional').get('actor', []))
                video_meta['作者'] = ','.join(meta.get('additional').get('writer', []))
                video_meta['导演'] = ','.join(meta.get('additional').get('director', []))
                video_meta['摘要'] = meta.get('additional').get('summary', '')

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
            utils.add_log(self.logger, 'info', '创建临时封面:', utils.POSTER_PATH)
            with open(utils.POSTER_PATH, 'wb') as f:
                f.write(image_data)

        if os.path.isfile(utils.POSTER_PATH):
            myname = socket.getfqdn(socket.gethostname())
            addr = socket.gethostbyname(myname)
            param = {
                'id': '{}'.format(sid),
                'type': '"{}"'.format(stype),
                'target': '"url"',
                'url': '"http://{}:{}/{}/{}"'.format(addr, utils.HTTP_SERVER_PORT, utils.IMG_CACHE_SUBDIR,
                                                     utils.POSTER_FILE),
            }
            json_res = self.post_request('entry.cgi', 'SYNO.VideoStation2.Poster', 'set', param)
            if os.path.isfile(utils.POSTER_PATH):
                utils.add_log(self.logger, 'info', '删除临时封面:', utils.POSTER_PATH)
                os.remove(utils.POSTER_PATH)
            return json_res and json_res.get('success')

    # 设置背景图
    def set_backdrop(self, stype, sid, image_data):
        if not stype or not sid or not image_data:
            return
        if os.path.isfile(utils.BACKDROP_PATH):
            os.remove(utils.BACKDROP_PATH)

        if image_data:
            utils.add_log(self.logger, 'info', '创建临时背景:', utils.BACKDROP_PATH)
            with open(utils.BACKDROP_PATH, 'wb') as f:
                f.write(image_data)

        if os.path.isfile(utils.BACKDROP_PATH):
            myname = socket.getfqdn(socket.gethostname())
            addr = socket.gethostbyname(myname)
            data = {
                'id': '{}'.format(sid),
                'type': '"{}"'.format(stype),
                'target': '"url"',
                'url': '"http://{}:{}/{}/{}"'.format(addr, utils.HTTP_SERVER_PORT, utils.IMG_CACHE_SUBDIR,
                                                     utils.BACKDROP_FILE),
                'keep_one': 'true',
            }
            json_res = self.post_request('entry.cgi', 'SYNO.VideoStation2.Backdrop', 'add', data)
            if os.path.isfile(utils.BACKDROP_PATH):
                utils.add_log(self.logger, 'info', '删除临时背景:', utils.BACKDROP_PATH)
                os.remove(utils.BACKDROP_PATH)
            return json_res.get('success')

    def set_video_info(self, meta):
        if not meta:
            return
        stype = meta.get('type')
        if not stype:
            return
        param = None

        if stype == 'home_video':
            param = {
                'library_id': '{}'.format(meta.get('library_id')),
                'target': '"video"',
                'id': '{}'.format(meta.get('id')),
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
                'library_id': '{}'.format(meta.get('library_id')),
                'target': '"video"',
                'id': '{}'.format(meta.get('id')),
                'title': '"{}"'.format(meta.get('电视节目标题', '')),
                'original_available': '"{}"'.format(utils.format_date_str(meta.get('发布日期', ''))),
                'metadata_locked': 'true',
                'summary': '"{}"'.format(meta.get('摘要', '')),
                'extra': '"null"',
                'update_tvshow': '""',
            }

        if stype == 'tvshow_episode':
            param = {
                'library_id': '{}'.format(meta.get('library_id')),
                'target': '"video"',
                'id': '{}'.format(meta.get('id')),
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
                'library_id': '{}'.format(meta.get('library_id')),
                'target': '"video"',
                'id': '{}'.format(meta.get('id')),
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
                'tvshow_extra': '"null"',
            }
        if not param:
            return
        json_res = self.post_request('entry.cgi', 'SYNO.VideoStation2.{}'.format(utils.get_library_API(stype)), 'edit',
                                     param)

        # print(json_res)

        return json_res.get('success')


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
