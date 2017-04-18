#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: syaofox@gmail.com
from urllib.parse import quote, urljoin

import re
from pyquery import PyQuery as pq
import utils
from spiders.base_spider import BaseSpider


class Kin8tengokuSpider(BaseSpider):
    def parse_url_search(self, res, stype='movie'):
        if not res:
            return

        result = utils.gen_metadata_struck(stype)
        try:

            doc = pq(res.text)

            title = doc('#mini-tabet > h2').text()

            if '标题' in result:
                result['标题'] = title
            if '电视节目标题' in result:
                result['电视节目标题'] = title
            if '集标题' in result:
                result['集标题'] = title

            result['级别'] = 'R18+'

            result['tag']['type'] = stype
            result['tag']['dital_url'] = res.url
            result['tag']['video_id'] = doc('#mini-tabet > div').text().strip('商品番号: ')
            result['tag']['tip'] = doc('#titlebox > ul:nth-child(4) > li:nth-child(1) > a').text()

            poster_url = doc('#titlebox > div.list-cover > img').attr('src')
            if poster_url:
                result['tag']['poster'] = self.download_page_request(poster_url).content

        except Exception:
            pass

        return result

    def parse_search_html(self, res, stype):
        if not res:
            return
        html = res.text
        main_url = res.url
        doc = pq(html)

        next_page = doc('#sub_main > div.listpage > ul > li.next > a')
        if next_page.text() == '次へ »':
            self.add_urls(urljoin(main_url,next_page.attr('href')))

        try:
            total = doc('#sub_main > p').text()
            total = re.search('(\d+)',total).group(1)
            yield int(total)
        except Exception:
            pass

        divs = doc('#sub_main > div.movie_list').items()
        for div in divs:
            result = utils.gen_metadata_struck(stype)
            title = div('div.movielistphoto1 > a > img').attr('alt')
            if '标题' in result:
                result['标题'] = title
            if '电视节目标题' in result:
                result['电视节目标题'] = title
            if '集标题' in result:
                result['集标题'] = title
            result['级别'] = 'R18+'
            result['tag']['type'] = stype
            result['tag']['dital_url'] =urljoin(main_url, div('div.movielistphoto1 > a').attr('href'))
            result['tag']['video_id'] = re.search(r'/(\d+)/index',result['tag']['dital_url']).group(1)
            result['tag']['tip'] = div('div.movielisttext01 > a').text()
            poster_url = div('div.movielistphoto1 > a > img').attr('src')
            if poster_url:
                result['tag']['poster'] = self.download_page_request(poster_url).content
                result['tag']['xy'] = (80,40)
            yield result

    def search(self, keyword, stype):
        if keyword.startswith('http'):
            res = self.download_page_request(keyword)

            yield self.parse_url_search(res, stype)
        else:
            self.add_urls(
                'http://www.kin8tengoku.com/search/?q={}&category_search_type=and&flag_match_type=0'.format(quote(keyword,encoding='euc-jp')))
            while self.has_url():
                url = self.get_urls()
                if url:
                    res = self.download_page_request(url)
                    if res:
                        for each in self.parse_search_html(res, stype):
                            yield each
                    else:
                        print('搜索失败')


if __name__ == '__main__':
    test = Kin8tengokuSpider('kin8')
    for each in test.search('初の日本刀','movie'):
        print(each)