from time import sleep
from urllib.parse import urljoin

import os
import requests
from PyQt5.QtCore import QObject
from requests import RequestException
from requests_cache import CachedSession

import utils
from models.cache import DownCache
import logging


class BaseSpider:
    def __init__(self, name):
        self.name = name

        self.RequestSession = CachedSession(cache_name=os.path.join(utils.CACHE_PATH,'spider_cache'),include_get_headers=True,expire_after=utils.SPIDER_CACHE_KEEP_TIME)
        self.RequestSession.hooks = {'response': self.make_throttle_hook(utils.SPIDER_DOWNLOAD_SLEEP_TIME)}
        self.RequestSession.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'})
        self.urls = set()
        self.oldurls = set()
        self.stoped = False
        self.count = 0
        self.logger = logging.getLogger('spider:{}'.format(name))

        self.retry = 0

    def make_throttle_hook(self,timeout=1.0):
        """
        Returns a response hook function which sleeps for `timeout` seconds if
        response is not cached
        """

        def hook(response, *args, **kwargs):
            if not getattr(response, 'from_cache', False):
                print('sleeping')
                sleep(timeout)
            return response

        return hook

    def spdider_login(self):
        pass

    def clear(self):
        self.urls.clear()
        self.oldurls.clear()
        self.stoped = False
        self.count = 0

    def add_urls(self, url):
        if not url:
            return
        if url not in self.oldurls and url not in self.urls:
            self.urls.add(url)

    def get_urls(self):
        if self.has_url():
            url = self.urls.pop()
            self.oldurls.add(url)
            return url
        else:
            return None

    def has_url(self):
        return len(self.urls) > 0

    def download_page_request(self, url, retry=0):
        if self.stoped:
            return None
        if not url:
            utils.add_log(self.logger,'error','Url为空', url)
            return

        try:
            res = self.RequestSession.get(url, timeout=10)
            if res.status_code == 200:
                self.RequestSession.headers.update({'referer': res.url, 'Referer': res.url})
                return res
            else:
                if retry >= utils.RETRYMAX:

                    utils.add_log(self.logger, 'info', 'Url下载出错，重试达到最大数', url)
                    return None
                else:
                    retry += 1

                    utils.add_log(self.logger, 'info', 'Url下载出错{}，重试{}'.format(url, retry))
                    sleep(5)
                    return self.download_page_request(url,  retry)
        except RequestException:
            if retry >= utils.RETRYMAX:
                utils.add_log(self.logger, 'info', 'Url下载出错，重试达到最大数', url)
                return None
            else:
                retry += 1
                utils.add_log(self.logger, 'info', 'Url下载出错{}，重试{}'.format(url, retry))
                sleep(5)
                return self.download_page_request(url, retry)


if __name__ == '__main__':
    a = BaseSpider('test')
    re = a.download_page_request('http://pics.dmm.co.jp/digital/video/mide00419/mide00419-9.jpg')
    print(re.from_cache)
    print(re.headers)
    print(re.cookies)
    print(len(re.content))
    re = a.download_page_request('http://pics.dmm.co.jp/digital/video/mide00419/mide00419-3.jpg')
    print(re.from_cache)
    print(re.headers)
    print(re.cookies)
    print(len(re.content))

    # import requests_cache
    #
    # requests_cache.install_cache(os.path.join(utils.CACHE_PATH,'spider_cache'),expire_after=600000)
    # ss = CachedSession(os.path.join(utils.CACHE_PATH, 'spider_cache'), expire_after=600000)
    #
    # # ss = requests.session()
    # ss.headers.update({
    #     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    # })
    #
    # re = ss.get('http://www.win-rar.com/fileadmin/winrar-versions/winrar-x64-531.exe', verify=False)
    # print(re.headers)
    # print(re.cookies)
    # print(len(re.content))
