#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from time import sleep

import re
from pyquery import PyQuery as pq
import utils
from spiders.base_spider import BaseSpider


class AventertainmentsSpider(BaseSpider):
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

        next_page = doc('#main-list-header > div.row2 > div.pagination > ol > a:last-child')
        if next_page.text() == '次へ' and next_page.attr('class') != 'backnext disablelink':
            self.add_urls(next_page.attr('href'))

        try:
            total = doc('#main-list-header > div.row2 > div.column1 > strong:nth-child(1)').text()
            yield int(total)
        except Exception:
            pass

        trs = doc('div.main-unit2 tr td table').items()
        for tr in trs:
            result = utils.gen_metadata_struck(stype)

            title = tr('h4').text()

            if '标题' in result:
                result['标题'] = title
            if '电视节目标题' in result:
                result['电视节目标题'] = title
            if '集标题' in result:
                result['集标题'] = title
            result['级别'] = 'R18+'

            result['tag']['type'] = stype
            result['tag']['dital_url'] = tr('h4 a').attr('href')
            pa = re.search(r'商品番号:(?P<video_id>.+?)<br/>.*発売日:(?P<tip>\d{2}/\d{2}/\d{4})<br/>', tr.html(), re.S)

            result['tag']['video_id'] = pa.group('video_id')
            result['tag']['tip'] = pa.group('tip')

            poster_url = tr('div.list-product img').attr('src')
            if poster_url:
                result['tag']['poster'] = self.download_page_request(poster_url).content
            yield result

    def search(self, keyword, stype):
        if keyword.startswith('http'):
            res = self.download_page_request(keyword)

            yield self.parse_url_search(res, stype)
        else:
            self.add_urls(
                'http://www.aventertainments.com/search_Products.aspx?languageID=2&dept_id=29&keyword={}&searchby=keyword&HowManyRecords=60'.format(
                    keyword))
            while self.has_url():
                url = self.get_urls()
                if url:
                    res = self.download_page_request(url)
                    if res:
                        for each in self.parse_search_html(res, stype):
                            yield each
                    else:
                        print('搜索失败')
            sleep(0.1)

    def parse_dital(self, html, meta):
        if not html or not meta: return
        doc = pq(html)

        try:
            date = utils.format_date_str(re.search(r'(\d{1,2}/\d{1,2}/\d{4})',
                                                   doc('#titlebox > ul:nth-child(4) > li:nth-child(5)').text()).group(
                1))
            if '发布日期' in meta:
                meta['发布日期'] = date
            if '发布日期(电视节目)' in meta:
                meta['发布日期(电视节目)'] = date
            if '发布日期(集)' in meta:
                meta['发布日期(集)'] = date
        except AttributeError:
            pass

        try:
            des = doc('#titlebox > div:nth-child(12) > p').text()

            meta['摘要'] = des.strip()
            meta['标语'] = meta['摘要'][:30]
        except AttributeError:
            pass

        try:
            if not meta['摘要']:
                des = doc('#titlebox > div:nth-child(11) > p').text()

                meta['摘要'] = des.strip()
                meta['标语'] = meta['摘要'][:30]
        except AttributeError:
            pass

        try:
            genlst = []
            genres = doc('#detailbox a').items()
            genlst = [genre.text().strip() for genre in genres]

            groups = doc('#titlebox > ul:nth-child(4) > li:nth-child(3) > a').items()
            genlst.extend([group.text().strip() for group in groups])

            meta['类型'] = ','.join(genlst)
        except AttributeError:
            pass

        try:
            actors = doc('#titlebox > ul:nth-child(4) > li:nth-child(1) a').items()
            meta['演员'] = ','.join([actor.text().strip() for actor in actors])
        except AttributeError:
            pass

        try:
            producers = doc('#titlebox > ul:nth-child(4) > li:nth-child(2) > a').items()
            meta['作者'] = ','.join([producer.text().strip() for producer in producers])
        except AttributeError:
            pass

        try:
            poster_data = self.download_page_request(doc('#CoverImage').attr('src')).content
            meta['tag']['backdrop'] = utils.tim_img_bytes(poster_data)
            meta['tag']['poster'] = utils.create_poster(meta['tag']['backdrop'])
        except AttributeError:
            pass
        yield meta

        try:
            # 缩略图
            sample_url = doc(
                '#TabbedPanels1 > div > div.TabbedPanelsContent.TabbedPanelsContentVisible > a > img').attr('src')
            yield self.download_page_request(sample_url).content

        except Exception:
            pass

    def dital(self, url, meta):
        res = self.download_page_request(url)
        if res:
            return self.parse_dital(res.text, meta)


if __name__ == '__main__':
    test = AventertainmentsSpider('av')
    res = test.download_page_request(
        'http://www.aventertainments.com/product_lists.aspx?product_id=96132&languageID=2&dept_id=29')

    x = test.parse_dital(res.text, utils.gen_metadata_struck('movie'))
    for each in x:
        print(each)
