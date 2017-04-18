#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: syaofox@gmail.com
import re
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
from collections import OrderedDict

import utils
from spiders.base_spider import BaseSpider


class Data18Spider(BaseSpider):
    def parse_search_html(self, res, stype):
        if not res:
            return

        relock = re.search(r'<a href="(.*?)">Click here to continue\.\.\.</a>', res.text)
        if relock:
            self.download_page_request(relock.group(1))
            self.add_log('parse_search_html 重置:', relock.group(1))
            self.add_urls(relock.group(1), True)
            return

        metas = []
        pattern = re.compile(r'<div style="float: left;.*?(\d{4}-\d{2}-\d{2}).*?'
                             r'<a href="(http://.*?)">.*?'
                             r'<img src="(http://.*?)".*?style=".*?'
                             r'title="(.*?)".*?</div>'

                             r'|'
                             r'<div class="bscene genmed".*?</b>(.*?\d{2}, \d{4}.*?)</p>'
                             r'<p class="line1">.*?<a href="(http://.*?)">.*?'
                             r'<img src="(http://.*?)".*?'
                             r'title="(.*?)".*?'
                             r'.*?</div>',
                             re.S)
        meta_movies = re.findall(pattern, res.text)
        if meta_movies:
            metas.extend(meta_movies)

        pattern2 = re.compile(r'<div class="bscene genmed".*?</b>(.*?\d{2}.*?\d{4}.*?)</p>.*?'
                              r'<p class="line1">.*?<a href="(http://.*?)">.*?'
                              r'<img src="(http://.*?)".*?'
                              r'title="(.*?)".*?'
                              r'.*?</div>', re.S)

        metas_contens = re.findall(pattern2, res.text)
        if metas_contens:
            metas.extend(metas_contens)

        for meta in metas:
            if self.stoped:
                break
            result = utils.gen_metadata_struck(stype)
            try:
                if '标题' in result:
                    result['标题'] = meta[3].strip()
                if '电视节目标题' in result:
                    result['电视节目标题'] = meta[3].strip()
                if '集标题' in result:
                    result['集标题'] = meta[3].strip()
            except Exception as e:
                self.add_log('parse_search_html 抓取标题错误:', e, level='error')

            result['tag']['type'] = stype
            result['tag']['dital_url'] = meta[1].strip()
            result['tag']['video_id'] = re.search(r'/(\d+)', meta[1]).group(1)

            result['tag']['poster'] = utils.tim_img_bytes(self.download_page_request(meta[2]).content)
            result['tag']['total'] = 0
            str = re.match(r'\s*(\w{3}).*?( \d{2}, \d{4})', meta[0], re.IGNORECASE)
            if str:
                result['tag']['tip'] = utils.format_date_str(str.group(1) + str.group(2))
            else:
                result['tag']['tip'] = utils.format_date_str(meta[0].strip())
            yield result

    def search(self, keyword, stype):
        if keyword.startswith('http'):
            res = self.download_page_request(keyword)
            meta = utils.gen_metadata_struck(stype)
            search_type = re.search(r'http://www\.data18\.com/(.*)/\d+', keyword).group(1)

            findeds = self.parse_dital(res.text, meta, search=True, types=search_type)

            for finded in findeds:
                if isinstance(finded, OrderedDict):
                    finded['tag']['type'] = stype
                    finded['tag']['dital_url'] = keyword

                    yield finded
        else:
            self.add_urls('http://www.data18.com/search/?k={}'.format(keyword))
            while self.has_url():
                url = self.get_urls()
                if url:
                    res = self.download_page_request(url)
                    if res:
                        for each in self.parse_search_html(res, stype):
                            yield each
                    else:
                        self.add_log('搜索失败')

    def dital(self, url, meta):
        try:
            stype = re.search(r'http://www\.data18\.com/(.*)/\d+', url).group(1)
            res = self.download_page_request(url)
            if res:
                return self.parse_dital(res.text, meta, types=stype, url=url)
        except Exception:
            pass

    def parse_thumbel_page(self, father_url):
        try:

            pa = re.search('(http://.*/)(\d+)', father_url)
            count = int(pa.group(2))
            http = pa.group(1)

            samples = ['{}{:0>2d}'.format(http, x) for x in range(1, count + 1)]
            if samples:
                for url in samples:
                    res = self.download_page_request(url, referer=url)
                    if res:
                        try:
                            soup = BeautifulSoup(res.text, 'lxml')
                            img_url = soup.select_one('#post_view > a > img').get('src')
                            img_data = self.download_page_request(img_url, res.url)
                            if img_data:
                                yield img_data.content
                        except Exception:
                            pass
        except Exception:
            pass

    def parse_dital(self, html, meta, types='movie',
                    search=False,
                    url=''):
        if not html or not meta: return
        relock = re.search(r'<a href="(.*?)">Click here to continue\.\.\.</a>', html)
        if relock:
            res = self.RequestSession.get((relock.group(1)), timeout=utils.DOWN_TIME_OUT)
            self.add_log('parse_search_html 重置:', relock.group(1))
            if res == 200:
                html = res.text
            else:
                return

        soup = BeautifulSoup(html, "lxml")

        if types == 'movies':
            try:
                title = soup.select_one('#centered > div.p8 > div:nth-of-type(1) > h1').text
                if '标题' in meta:
                    meta['标题'] = title
                if '电视节目标题' in meta:
                    meta['电视节目标题'] = title
                if '集标题' in meta:
                    meta['集标题'] = title
            except Exception:
                pass

            div_main = soup.select_one('#centered > div.p8 > div:nth-of-type(7) > div')

            is_backdrop = re.search('(Click to Enlarge Front & Back Cover)', div_main.text, re.S) is not None
            try:
                post_url = div_main.select_one('div:nth-of-type(1) > a').get('href')
                if is_backdrop:
                    meta['tag']['backdrop'] = utils.tim_img_bytes(self.download_page_request(post_url).content)
                    meta['tag']['poster'] = utils.create_poster(meta['tag']['backdrop'])
                else:
                    meta['tag']['poster'] = utils.tim_img_bytes(self.download_page_request(post_url).content)
                    backdrop_url = div_main.select_one('div:nth-of-type(1) > p > a').get('href')
                    meta['tag']['backdrop'] = utils.tim_img_bytes(self.download_page_request(backdrop_url).content)
                    meta['tag']['backdrop'] = utils.merge_image(meta['tag']['poster'], meta['tag']['backdrop'])
            except Exception:
                pass

            meta['级别'] = 'R18+'

            try:
                year = div_main.select_one('div.gen12 > p:nth-of-type(1)').text
                year = re.search(r'Release date: (.*?\d{4})', year)
                if not year:
                    year = div_main.select_one('div.gen12 > p:nth-of-type(2)').text
                    year = re.search(r'Release date: (.*?\d{4})', year)

                year = year.group(1)
                if '发布日期' in meta:
                    meta['发布日期'] = utils.format_date_str(year)
                if '发布日期(电视节目)' in meta:
                    meta['发布日期(电视节目)'] = utils.format_date_str(year)
                if '发布日期(集)' in meta:
                    meta['发布日期(集)'] = utils.format_date_str(year)


            except Exception:
                pass

            try:
                meta['摘要'] = div_main.select_one('div.gen12 > p.gen12').text.strip().strip('Description:')
                meta['标语'] = meta['摘要'][:30]
            except Exception:
                pass

            try:
                g_str = re.search('<b>Categories:</b>(.*?)<b>Description:', str(div_main), re.S).group(1)
                geres = []
                geres_a = re.findall(r'<a href=".*?">(.*?)</a>', g_str, re.S)
                if geres_a:
                    geres.extend(geres_a)
                geres_b = re.findall(r'<span class="gensmall">(.*?)</span>', g_str, re.S)
                if geres_b:
                    geres.extend(geres_b)
                geres = [a for a in filter(lambda x: x.find(':') < 0, geres)]
                meta['类型'] = ','.join(geres)
            except Exception:
                pass

            try:
                actor_div = soup.select('#centered > div.p8 > div:nth-of-type(10) > div > div > div')
                actors = [actor.text.strip() for actor in actor_div]
                actor_more = soup.select('#centered > div.p8 > div:nth-of-type(10) > div > p:nth-of-type(2) > a')
                if actor_more:
                    actors.extend([actor.text.strip() for actor in actor_more])
                meta['演员'] = ','.join(actors)
            except Exception:
                pass

            try:
                w_d = div_main.select_one('div.gen12 > p:nth-of-type(2)')
                writers = re.search(r'<b>(?:Site|Studio):</b> (.*?) \| <b>Director:</b>(.*?)</p>', str(w_d), re.S)
                if not writers:
                    w_d = div_main.select_one('div.gen12 > p:nth-of-type(3)')
                    writers = re.search(r'<b>(?:Site|Studio):</b> (.*?) \| <b>Director:</b>(.*?)</p>', str(w_d), re.S)

                if writers:
                    if writers.group(1):
                        writer = writers.group(1)
                        writer_a = re.search(r'<a.*?>(.*)</a>', writer)
                        if writer_a:
                            writer = writer_a.group(1)
                        meta['作者'] = ','.join([writer.strip()])

                    if writers.group(2):
                        director = writers.group(2)
                        director_a = re.search(r'<a.*?>(.*)</a>', director)
                        if director_a:
                            director = director_a.group(1)
                        meta['导演'] = ','.join([director.strip()])

            except Exception:
                pass

            yield meta

            # 缩略图
            if not search:
                try:
                    soup = BeautifulSoup(html, 'lxml')
                    samples = soup.select('#centered > div.p8 > div:nth-of-type(15) > a')
                    sample = samples[-1].get('href')
                    for im in self.parse_thumbel_page(sample):
                        yield im
                except Exception:
                    pass
        elif types == 'content':
            doc = pq(html)
            try:
                title = doc('#centered > div.p8 > div:nth-child(1) > h1').text()
                if '标题' in meta:
                    meta['标题'] = title
                if '电视节目标题' in meta:
                    meta['电视节目标题'] = title
                if '集标题' in meta:
                    meta['集标题'] = title
            except Exception:
                pass

            try:
                post_url = doc('#moviewrap > img').attr('src')

                meta['tag']['backdrop'] = utils.tim_img_bytes(self.download_page_request(post_url).content)
                meta['tag']['poster'] = utils.create_poster(meta['tag']['backdrop'], middle=True)

            except Exception:
                pass

            meta['级别'] = 'R18+'

            try:

                year = doc('#centered > div.p8 > div:nth-child(7) > div:nth-child(3) > p:nth-child(2) > span > a')
                year = year.text()

                if '发布日期' in meta:
                    meta['发布日期'] = utils.format_date_str(year)
                if '发布日期(电视节目)' in meta:
                    meta['发布日期(电视节目)'] = utils.format_date_str(year)
                if '发布日期(集)' in meta:
                    meta['发布日期(集)'] = utils.format_date_str(year)


            except Exception:
                pass

            try:
                meta['摘要'] = doc(
                    '#centered > div.p8 > div:nth-child(7) > div:nth-child(3) > div.gen12 > p').text().strip('Story:')
                meta['标语'] = meta['摘要'][:30]
            except Exception:
                pass
            #
            try:
                div_gener = doc(
                    '#centered > div.p8 > div:nth-child(7) > div:nth-child(3) > div:nth-child(5) > div').find(
                    'a').items()
                meta['类型'] = ','.join([x.text().strip() for x in div_gener])
            except Exception:
                pass

            if not meta['类型']:

                try:
                    div_gener = doc(
                        '#centered > div.p8 > div:nth-child(7) > div:nth-child(3) > div:nth-child(6) > div').find(
                        'a').items()
                    meta['类型'] = ','.join([x.text().strip() for x in div_gener])
                except Exception:
                    pass
            #
            try:
                actors_p = doc('#centered > div.p8 > div:nth-child(7) > div:nth-child(3) > p:nth-child(4)').find(
                    'a.bold').items()

                meta['演员'] = ','.join([x.text().strip() for x in actors_p])
            except Exception:
                pass
            try:
                if not meta['演员']:
                    actors_p = doc('#centered > div.p8 > div:nth-child(7) > div:nth-child(3) > p:nth-child(5)').find(
                        'a.bold').items()

                    meta['演员'] = ','.join([x.text().strip() for x in actors_p])
            except Exception:
                pass
            #
            try:
                d_w_p = doc('#centered > div.p8 > div:nth-child(7) > div:nth-child(3) > p:nth-child(3) > a').text()
                meta['作者'] = ','.join([d_w_p])
                meta['导演'] = ','.join([d_w_p])

            except Exception:
                pass

            yield meta

            # 缩略图
            if not search:
                try:
                    count = doc('#centered > div.p8 > div:nth-child(13) > div > p > b').text().strip('images').strip()
                    father = doc('#centered > div.p8 > div:nth-child(13) > div > div').find('a').attr('href')
                    pa = re.search('(http://.*/)(\d+)', father)

                    http = pa.group(1)
                    father_url = '{}{:0>2d}'.format(http, int(count))

                    for im in self.parse_thumbel_page(father_url):
                        yield im
                except Exception:
                    pass
