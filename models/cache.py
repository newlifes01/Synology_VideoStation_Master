#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import pickle
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
                self.logger.error('get_cache:{}'.format(e))

    def save_cache(self, data, filename='config'):
        try:
            if not filename or not data: return None
            cache_file_path = os.path.join(self.cache_path, filename)

            with open(cache_file_path, 'wb') as handle:
                pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

        except Exception as e:
            self.logger.error('save_cache:{}'.format(e))


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

    def get_cache(self, filename,subdir='url'):
        if not filename: return None
        cache_file_path = os.path.join(self.cache_path,subdir, self.__url_md5(filename))
        if self.__is_cache(cache_file_path):
            try:
                with open(cache_file_path, 'rb') as handle:
                    data = pickle.load(handle)
                    time_ticks = time()
                    load_time_ticks = data.get('time_ticks', 0.0)
                    keep_secs = data.get('keep_secs', utils.CACHE_KEEPTIME)
                    if time_ticks - load_time_ticks < keep_secs:
                        return data.get('data')
                    else:
                        self.logger.debug('过期删除:{}'.format(cache_file_path))
                        os.remove(cache_file_path)
                        return None
            except Exception as e:
                self.logger.error('get_data_cache', e)

    def save_cache(self, filename, data, keep_secs=utils.CACHE_KEEPTIME, subdir='url'):
        try:
            if not filename or not data: return None
            cache_file_path = os.path.join(self.cache_path,subdir)

            if not os.path.exists(cache_file_path):
                os.mkdir(cache_file_path)

            cache_file_path = os.path.join(self.cache_path, subdir, self.__url_md5(filename))

            time_ticks = time()
            save_data = {
                'time_ticks': time_ticks,
                'data': data,
                'keep_secs': keep_secs
            }
            self.logger.debug('save_cache:{}'.format(save_data))
            with open(cache_file_path, 'wb') as handle:
                pickle.dump(save_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            self.logger.error('save_cache:{}'.format(e))






if __name__ == '__main__':
    cache = DownCache()
    # cache.save_cache('1','xx')
    print(cache.get_cache('2'))
