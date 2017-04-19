#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: syaofox@gmail.com
from urllib.parse import urljoin

import re
from pyquery import PyQuery

import utils
from spiders.base_spider import BaseSpider


class DvdkanojyoSpider(BaseSpider):
    def parse_url_search(self, res, stype='movie'):
        if not res:
            return
        res.encoding = 'utf-8'
        result = utils.gen_metadata_struck(stype)
        try:

            doc = PyQuery(res.text)
            title = doc('#contents > form > div.detailed_title').text()
            if title:
                if '标题' in result:
                    result['标题'] = title
                if '电视节目标题' in result:
                    result['电视节目标题'] = title
                if '集标题' in result:
                    result['集标题'] = title

                result['级别'] = 'R18+'

                result['tag']['type'] = stype
                result['tag']['dital_url'] = res.url
                result['tag']['video_id'] = re.search(r'id=(\d+)', result['tag']['dital_url']).group(1)
                result['tag']['tip'] = doc('#contents > form > div.item_detail > ul > li:nth-child(2) > a').text()
                poster_url = urljoin(res.url, doc('#contents > form > div.item_detail > div.item600 > img').attr('src'))
                if poster_url:
                    result['tag']['backdrop'] = utils.tim_img_bytes(self.download_page_request(poster_url).content)
                    result['tag']['poster'] = utils.create_poster(result['tag']['backdrop'])
        except Exception:
            pass

        return result

    def parse_search_html(self, res, stype):
        if not res:
            return
        res.encoding = 'utf-8'
        html = res.text
        main_url = res.url
        doc = PyQuery(html)

        next_page = doc('#pagenation li.next a')
        if next_page.text() == '› ›':
            self.add_urls(urljoin(main_url, next_page.attr('href')))

        try:
            total = doc('#contents > div.message').text()
            total = re.search('(\d+)', total).group(1)
            yield int(total)
        except Exception:
            pass

        divs = doc('#contents > form > div.item_box.fixHeight > div').items()
        for div in divs:
            result = utils.gen_metadata_struck(stype)
            title = div('p > a').text()
            if title:
                if '标题' in result:
                    result['标题'] = title
                if '电视节目标题' in result:
                    result['电视节目标题'] = title
                if '集标题' in result:
                    result['集标题'] = title
                result['级别'] = 'R18+'
                result['tag']['type'] = stype
                result['tag']['dital_url'] = urljoin(main_url, div('a').attr('href'))
                result['tag']['video_id'] = re.search(r'id=(\d+)', result['tag']['dital_url']).group(1)
                # result['tag']['tip'] = div('span.movie-actor > a > span').text()
                poster_url = urljoin(main_url, div('a > img').attr('src'))
                if poster_url:
                    result['tag']['poster'] = self.download_page_request(poster_url).content
                yield result

    def search(self, keyword, stype):
        if keyword.startswith('http'):
            res = self.download_page_request(keyword)
            yield self.parse_url_search(res, stype)
        else:

            res = self.download_page_request('http://dvdkanojyo.com/pc/search/index.php', meth='POST',
                                             data={'mode': 'kyefind', 'kye': keyword, 'submit': '検索'})
            if res:
                for each in self.parse_search_html(res, stype):
                    yield each

            while self.has_url():
                url = self.get_urls()
                if url:
                    res = self.download_page_request(url)
                    if res:
                        for each in self.parse_search_html(res, stype):
                            yield each
                    else:
                        print('搜索失败')

    def parse_dital(self, html, meta):
        if not html or not meta: return
        doc = PyQuery(html)
        try:
            title = doc('#contents > form > div.detailed_title').text()

            if '标题' in meta:
                meta['标题'] = title
            if '电视节目标题' in meta:
                meta['电视节目标题'] = title
            if '集标题' in meta:
                meta['集标题'] = title
        except AttributeError:
            pass

        # try:
        #     date = doc('#main-content > div.main-content-movieinfo > div.movie-info > dl:nth-child(3) > dd').text()
        #     if '发布日期' in meta:
        #         meta['发布日期'] = date
        #     if '发布日期(电视节目)' in meta:
        #         meta['发布日期(电视节目)'] = date
        #     if '发布日期(集)' in meta:
        #         meta['发布日期(集)'] = date
        # except AttributeError:
        #     pass

        try:

            meta['摘要'] = doc('#contents > form > div.item_detail > div:nth-child(5)').text().strip()
            meta['标语'] = meta['摘要'][:30]
        except AttributeError:
            pass

        try:
            meta['类型'] = ','.join([genre.text() for genre in
                                   doc('#contents > form > div.item_detail > ul > li:nth-child(4) > a').items()])

        except AttributeError:
            pass

        try:
            actors = doc('#contents > form > div.item_detail > ul > li:nth-child(2) > a').items()
            meta['演员'] = ','.join([actor.text().strip() for actor in actors])
        except AttributeError:
            pass

        try:
            writers = doc('#contents > form > div.item_detail > ul > li:nth-child(3) > a').items()
            meta['作者'] = ','.join([writer.text().strip() for writer in writers])
        except AttributeError:
            pass

        # try:
        #     starts = doc('#main-content > div.main-content-movieinfo > div.movie-info > dl:nth-child(5) > dd').text()
        #     if starts:
        #
        #         meta['评级'] = str(20*len(starts))
        # except AttributeError:
        #     pass

        try:
            poster_url = urljoin(meta.get('tag').get('dital_url'),
                                 doc('#contents > form > div.item_detail > div.item600 > img').attr('src'))
            if poster_url:
                meta['tag']['backdrop'] = utils.tim_img_bytes(self.download_page_request(poster_url).content)
                meta['tag']['poster'] = utils.create_poster(meta['tag']['backdrop'])
        except AttributeError:
            pass
        yield meta

        try:
            # 缩略图
            sample_urls = doc('#contents > form > div.item_cap > img').items()
            for sample_url in sample_urls:
                nail_url = sample_url.attr('src')
                if nail_url:
                    nail_url = urljoin(meta.get('tag').get('dital_url'), nail_url)

                    yield self.download_page_request(nail_url).content

        except Exception:
            pass

    def dital(self, url, meta):
        res = self.download_page_request(url)
        if res:
            res.encoding = 'utf-8'
            return self.parse_dital(res.text, meta)


if __name__ == '__main__':
    test = DvdkanojyoSpider('DvdkanojyoSpider')
    aa = test.search('http://dvdkanojyo.com/pc/detail/index.php?id=48649', 'movie')
    for each in aa:
        # print(each)
        if not isinstance(each, int):
            print(each.get('tag').get('dital_url'))
            for dital in test.dital(each.get('tag').get('dital_url'), each):
                print(dital)
            break
