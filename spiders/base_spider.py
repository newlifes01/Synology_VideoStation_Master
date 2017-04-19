import logging
from time import sleep, time

import OpenSSL
import requests
from requests import RequestException
import utils
from models.cache import DownCache


class BaseSpider:
    def __init__(self, name):
        self.name = name
        self.cache = DownCache(table_name='spider_cache')
        self.RequestSession = requests.session()  # CachedSession(cache_name=os.path.join(utils.CACHE_PATH,'spider_cache'),include_get_headers=True,expire_after=utils.SPIDER_CACHE_KEEP_TIME)
        self.RequestSession.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'})
        self.urls = set()
        self.oldurls = set()
        self.logger = logging.getLogger('spider:{}'.format(name))
        self.stoped = False

    def add_log(self, *msg, level='info'):
        utils.add_log(self.logger, level, msg)

    def spdider_login(self):
        pass

    def clear(self):
        self.urls.clear()
        self.oldurls.clear()

    def add_urls(self, url, fource=False):
        if not url:
            return
        if (url not in self.oldurls and url not in self.urls) or fource:
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

    def download_page_request(self, url, retry=0, referer='',meth='GET',data=''):
        if not url or self.stoped:
            utils.add_log(self.logger, 'error', 'Url为空', url)
            return

        try:
            if meth != 'POST':
                res = self.cache.get_cache(url)
                if res:
                    return res

            if meth == 'GET':
                res = self.RequestSession.get(url, timeout=utils.DOWN_TIME_OUT)
            elif meth == 'POST' and data:
                res = self.RequestSession.post(url, timeout=utils.DOWN_TIME_OUT,data=data)
            else:
                return None
            sleep(utils.SPIDER_DOWNLOAD_SLEEP_TIME)
            if res.status_code == 200:
                if referer == '':
                    referer = res.url
                self.RequestSession.headers.update({'referer': referer, 'Referer': referer})
                if meth != 'POST':
                    utils.add_log(self.logger, 'info', 'save_cache expire:', url, )
                    if utils.IMG_CACHE_KEEP_INFINITE and utils.IsValidImage(res.content):
                        self.cache.save_cache(url, res, expire_time=0, mtime=0)
                        self.add_log('永久缓存', url)
                    else:
                        self.cache.save_cache(url, res, time())
                return res
            else:
                if retry >= utils.RETRYMAX:
                    utils.add_log(self.logger, 'info', 'Url下载出错，重试达到最大数', url)
                    return None
                else:
                    retry += 1

                    utils.add_log(self.logger, 'info', 'Url下载出错{}，重试{}'.format(url, retry))
                    sleep(5)
                    return self.download_page_request(url, retry)
        except (RequestException,OpenSSL.SSL.Error):
            if retry >= utils.RETRYMAX:
                utils.add_log(self.logger, 'info', 'Url下载出错，重试达到最大数', url)
                return None
            else:
                retry += 1
                utils.add_log(self.logger, 'info', 'Url下载出错{}，重试{}'.format(url, retry))
                sleep(5)
                return self.download_page_request(url, retry)

    def parse_page(self, respone):
        pass

    def search(self, keyword, stype):
        pass

    def dital(self, url, meta):
        pass


if __name__ == '__main__':
    a = BaseSpider('test')
    re = a.download_page_request('https://img3.doubanio.com/view/movie_poster_cover/lpst/public/p2454282762.webp')
    print(re.headers)
    print(re.cookies)
    print(len(re.content))
