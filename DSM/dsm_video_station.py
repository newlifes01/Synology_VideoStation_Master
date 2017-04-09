#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import requests
from PyQt5.QtCore import QThread

from models.cache import ConfigCache


class DSMAPI(QThread):
    def __init__(self, session, ip):
        super().__init__()
        self.logger = logging.getLogger('DSMAPI')
        self.ip = ip
        self.session = session
        self.cache = ConfigCache()
        self.set_cookie_form_cache()

    def __load_cookie(self):
        login_data = self.cache.get_cache()
        if login_data:
            cookies = login_data.get('cookies')
            ip = login_data.get('ip')
            return ip, cookies
        return '',{}

    def __save_cookie(self):
        self.cache.save_cache({
            'cookies':requests.utils.dict_from_cookiejar(self.session.cookies),
            'ip':self.ip
        })

    def post_request(self, cgi, api='', method='', extra=None, bytes=False):
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

    def set_cookie_form_cache(self):
        ip, cookies = self.__load_cookie()
        if not cookies or not ip:
            return False
        else:
            self.ip = ip
            self.logger.debug('设置登陆信息')
            requests.utils.add_dict_to_cookiejar(self.session.cookies, cookies)

    def check_login_status(self):
        if not self.ip:
            return False
        url = 'http://{}/{}'.format(self.ip, 'webman/login.cgi?enable_syno_token=yes')
        res = self.session.post(url)
        if res.status_code == 200:
            json_res = res.json()
            if json_res and json_res.get('success'):
                self.__save_cookie()
                self.logger.debug('保存登陆信息')
                return True
        return False

    def login_dsm(self, account, password):
        if not account or not password:
            return False
        json_res = self.post_request('auth.cgi', 'SYNO.API.Auth', 'login', {'account': account, 'passwd': password})
        if json_res and json_res.get('success'):
            self.__save_cookie()
            return True


if __name__ == '__main__':
    session = requests.session()
    # requests.utils.add_dict_to_cookiejar(session.cookies, {
    #     'stay_login': '1',
    #     'id': 'ez6HTNdVuGbhs1610NEN304901'
    # })

    dsm = DSMAPI(session,'192.168.2.97:5000')


    while not dsm.check_login_status():
        if dsm.login_dsm('syaofox','090109'):
            print('已登陆')