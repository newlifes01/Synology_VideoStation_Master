import logging
from time import sleep, time
import requests
from requests import RequestException
import utils
from models.cache import DownCache

class BaseSpider:
    def __init__(self, name):
        self.name = name
        self.cache = DownCache(table_name='spider_cache')
        self.RequestSession = requests.session() #CachedSession(cache_name=os.path.join(utils.CACHE_PATH,'spider_cache'),include_get_headers=True,expire_after=utils.SPIDER_CACHE_KEEP_TIME)
        self.RequestSession.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'})
        self.urls = set()
        self.oldurls = set()
        self.logger = logging.getLogger('spider:{}'.format(name))

    def spdider_login(self):
        pass

    def clear(self):
        self.urls.clear()
        self.oldurls.clear()

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
        if not url:
            utils.add_log(self.logger,'error','Url为空', url)
            return

        head = self.RequestSession.head(url, timeout=utils.DOWN_TIME_OUT)
        try:
            if head.status_code == 200:
                modify_time = utils.format_time_stamp(head.headers.get('Last-Modified'))
                if not modify_time:
                    modify_time = utils.format_time_stamp(head.headers.get('last-modified'))
                if modify_time:
                    res = self.cache.get_cache(url,modify_time)
                else:
                    res = self.cache.get_cache(url)
                if res:
                    return res
        except Exception:
            pass

        try:
            res = self.RequestSession.get(url, timeout=utils.DOWN_TIME_OUT)
            sleep(utils.SPIDER_DOWNLOAD_SLEEP_TIME)
            if res.status_code == 200:
                self.RequestSession.headers.update({'referer': res.url, 'Referer': res.url})
                modify_time = utils.format_time_stamp(res.headers.get('Last-Modified'))
                if not modify_time:
                    modify_time = utils.format_time_stamp(res.headers.get('last-modified'))

                if modify_time:
                    utils.add_log(self.logger, 'info', 'save_cache modify_time:', url,modify_time)
                    self.cache.save_cache(url,res,modify_time,0)
                else:
                    utils.add_log(self.logger, 'info', 'save_cache expire:', url, )
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

    def parse_page(self,respone):
        pass

    def search(self,keyword):
        pass

    def dital(self,url):
        pass


if __name__ == '__main__':
    a = BaseSpider('test')
    # re = a.download_page_request('http://pics.dmm.co.jp/digital/video/mide00419/mide00419-9.jpg')
    # print(re.headers)
    # print(re.cookies)
    # print(len(re.content))
    re = a.download_page_request('https://img3.doubanio.com/view/movie_poster_cover/lpst/public/p2454282762.webp')
    print(re.headers)
    print(re.cookies)
    print(len(re.content))
    # re = a.download_page_request('http://www.dmm.co.jp/digital/videoa/-/detail/=/cid=mide00419/')
    # print(re.headers)
    # print(re.cookies)
    # print(len(re.content))
    # re = a.download_page_request('http://pics.dmm.co.jp/digital/video/mide00419/mide00419-3.jpg')
    # print(re.from_cache)
    # print(re.headers)
    # print(re.cookies)
    # print(len(re.content))

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
