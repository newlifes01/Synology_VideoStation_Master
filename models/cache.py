#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import pickle
from datetime import datetime, timedelta
from time import time, sleep

import hashlib
import logging
import os
import sqlite3

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
    def __init__(self, table_name='cache'):
        self.table_name = table_name
        self.logger = logging.getLogger('DownCache')
        self.initDB()
        self.del_expire()

    def initDB(self):

        db = sqlite3.connect(utils.DSM_CACHE_PATH)
        cursor = db.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS {}(
                  name_hash VARCHAR(50),
                  add_time REAL,
                  expire REAL,
                  add_data BLOB
                  
                )
                '''.format(self.table_name))
            try:
                # cursor.execute('CREATE UNIQUE INDEX {}_name ON {} (name) '.format(self.table_name,self.table_name))
                cursor.execute(
                    'CREATE UNIQUE INDEX {}_name_uindex ON {} (name_hash) '.format(self.table_name, self.table_name))

            except sqlite3.OperationalError:
                pass
            db.commit()
        finally:
            cursor.close()
            db.close()

    def __url_md5(self, file_name):
        if not file_name: return
        md5 = hashlib.md5()
        md5.update(file_name.encode("utf-8"))
        return md5.hexdigest()

    def del_expire(self):
        db = sqlite3.connect(utils.DSM_CACHE_PATH)
        cursor = db.cursor()

        try:
            cursor.execute('SELECT * FROM {}'.format(self.table_name))

            rss = cursor.fetchall()

            for rs in rss:
                name, ntime, expire, data, = rs
                if expire > 0 and time() > expire:
                    cursor.execute('DELETE FROM {} WHERE name_hash=?'.format(self.table_name), (name,))
                    utils.add_log(self.logger, 'info', 'del_expire:', name)

            db.commit()
        except Exception as e:
            utils.add_log(self.logger, 'error', 'del_expire:', e)
        finally:
            cursor.close()
            db.close()

    def get_cache(self, filename, mtime=0):
        if not filename or mtime is None:
            return
        db = sqlite3.connect(utils.DSM_CACHE_PATH)
        cursor = db.cursor()
        try:
            cursor.execute('SELECT * FROM {} WHERE name_hash=?'.format(self.table_name), (self.__url_md5(filename),))

            rs = cursor.fetchone()
            if rs:
                name, ntime, expire, data, = rs
                now = time()
                if not name or ntime is None or not data:
                    return

                if (mtime == ntime and expire == 0) or (expire > 0 and now <= expire):

                    utils.add_log(self.logger, 'info', 'get_cache:', filename, mtime, expire)
                    return pickle.loads(data)

                else:
                    utils.add_log(self.logger, 'info', '删除过期缓存:', filename, mtime, expire)
                    cursor.execute('DELETE FROM {} WHERE name_hash=?'.format(self.table_name), (self.__url_md5(filename),))
                    return None

        except Exception as e:
            utils.add_log(self.logger, 'error', 'get_cache:', e)
        finally:
            cursor.close()
            db.close()

    def save_cache(self, filename, data, mtime, expire_time=utils.CACHE_KEEP_TIME):  # keep_secs=utils.CACHE_KEEPTIME,
        if not filename or not data or mtime is None:
            return
        db = sqlite3.connect(utils.DSM_CACHE_PATH)
        cursor = db.cursor()

        if expire_time != 0:
            expire = expire_time + time()
        else:
            expire = 0

        try:

            pdata = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)

            sql = "REPLACE INTO {} (name_hash,add_time, expire,add_data) VALUES (?,?,?,?)".format(self.table_name)
            cursor.execute(sql, (self.__url_md5(filename), mtime, expire, pdata))
            db.commit()
            utils.add_log(self.logger, 'info', 'save_cache', filename, mtime, expire)
        except Exception as e:
            utils.add_log(self.logger, 'error', 'save_cache', filename, mtime, expire, e)
        finally:
            cursor.close()
            db.close()


if __name__ == '__main__':
    timestr = '2017-01-27 03:47:18.349044'
    print(datetime.strptime(timestr, '%Y-%m-%d %H:%M:%S.%f'))
    timestr2 = 'Mon, 13 Mar 2017 00:16:37 GMT'
    print(datetime.strptime(timestr2, '%a, %d %b %Y %H:%M:%S %Z'))
