#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import pickle
from datetime import datetime
from time import time, sleep

import hashlib
import logging
import os

import utils

class ConfigCache(object):
    def __init__(self, cache_path=utils.CONFIG_PATH):
        self.cache_path = cache_path
        self.logger = logging.getLogger('ConfigCache')

        if not os.path.exists(cache_path):
            os.mkdir(cache_path)

    def __is_cache(self, cache_file_path):
        if not cache_file_path: return
        if os.path.exists(cache_file_path):
            return True
        return False

    def get_cache(self, filename='config'):
        if not filename: return None
        cache_file_path = os.path.join(self.cache_path, filename)
        if self.__is_cache(cache_file_path):
            try:
                with open(cache_file_path, 'rb') as handle:
                    return pickle.load(handle)
            except Exception as e:
                utils.add_log(self.logger, 'error', 'get_cache:', e)

    def save_cache(self, data, filename='config'):
        try:
            if not filename or not data: return None
            cache_file_path = os.path.join(self.cache_path, filename)

            with open(cache_file_path, 'wb') as handle:
                pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

        except Exception as e:
            utils.add_log(self.logger, 'error', 'save_cache:', e)


class DownCache(object):
    def __init__(self, cache_path=utils.CACHE_PATH):
        self.cache_path = cache_path
        self.logger = logging.getLogger('DownCache')

        if not os.path.exists(cache_path):
            os.mkdir(cache_path)

    def __url_md5(self, file_name):
        if not file_name: return
        md5 = hashlib.md5()
        md5.update(file_name.encode("utf-8"))
        return md5.hexdigest()

    def __is_cache(self, cache_file_path):
        if not cache_file_path: return
        if os.path.exists(cache_file_path):
            return True
        return False

    def get_cache(self, filename,mtime=0,subdir='url'):
        if not filename: return None
        cache_file_path = os.path.join(self.cache_path,subdir, self.__url_md5(filename))
        if self.__is_cache(cache_file_path):
            try:
                with open(cache_file_path, 'rb') as handle:
                    data = pickle.load(handle)
                    # time_ticks = time()
                    # load_time_ticks = data.get('time_ticks', 0.0)
                    # keep_secs = data.get('keep_secs', utils.CACHE_KEEPTIME)
                    # if time_ticks - load_time_ticks < keep_secs:
                    #     return data.get('data')
                    # else:
                    load_time_ticks = data.get('time_ticks', 0)
                    if mtime == load_time_ticks:
                        return data.get('data')
                    else:
                        utils.add_log(self.logger, 'info', '过期删除:', cache_file_path)
                        os.remove(cache_file_path)
                        return None
            except Exception as e:
                utils.add_log(self.logger, 'error', 'get_cache:', cache_file_path)

    def save_cache(self, filename, data, mtime, subdir='url'): #keep_secs=utils.CACHE_KEEPTIME,
        try:
            if not filename or not data: return None
            cache_file_path = os.path.join(self.cache_path,subdir)

            if not os.path.exists(cache_file_path):
                os.mkdir(cache_file_path)

            cache_file_path = os.path.join(self.cache_path, subdir, self.__url_md5(filename))

            # time_ticks = time()
            save_data = {
                'time_ticks': mtime,
                'data': data,
                # 'keep_secs': keep_secs
            }
            # self.logger.debug('save_cache:{}'.format(save_data))
            utils.add_log(self.logger, 'info', 'save_cache:', save_data)
            with open(cache_file_path, 'wb') as handle:
                pickle.dump(save_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            utils.add_log(self.logger, 'error', 'save_cache:', e)

# def datestr2secs(datestr):
#     tmlist = []
#     array = datestr.split(' ')
#     array1 = array[0].split('-')
#     array2 = array[1].split(':')
#     for v in array1:
#         tmlist.append(int(v))
#     for v in array2:
#         tmlist.append(int(v))
#     tmlist.append(0)
#     tmlist.append(0)
#     tmlist.append(0)
#     if len(tmlist) != 9:
#         return 0
#     return int(time.mktime(tmlist))


if __name__ == '__main__':
    timestr ='2017-01-27 03:47:18.349044'
    print(datetime.strptime(timestr,'%Y-%m-%d %H:%M:%S.%f'))
    timestr2 = 'Mon, 13 Mar 2017 00:16:37 GMT'
    print(datetime.strptime(timestr2, '%a, %d %b %Y %H:%M:%S %Z'))
