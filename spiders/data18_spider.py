#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: syaofox@gmail.com
import re
from bs4 import BeautifulSoup

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

            # result['tag']['backdrop'] = utils.tim_img_bytes(self.download_page_request(self.get_full_src(src_url)).content)
            result['tag']['poster'] = utils.tim_img_bytes(self.download_page_request(meta[2]).content)
            result['tag']['total'] = 0
            # result['tag']['tip'] = utils.format_date_str(meta[0].strip())
            str = re.match(r'\s*(\w{3}).*?( \d{2}, \d{4})', meta[0], re.IGNORECASE)
            if str:
                result['tag']['tip'] = utils.format_date_str(str.group(1) + str.group(2))
            else:
                result['tag']['tip'] = utils.format_date_str(meta[0].strip())
            yield result

    def parse_url_search(self, res, stype='movie'):
        if not res:
            return
        result = utils.gen_metadata_struck(stype)
        pattern = re.compile(r'<div style="float: left;.*?(\d{4}-\d{2}-\d{2}.*?)'
                             r'<a href="(http://.*?)">.*?'
                             r'<img src="(http://.*?)" style=".*?'
                             r'title="(.*?)".*?')
        metas = re.findall(pattern, res.text, re.S)
        try:
            for meta in metas:
                if '标题' in result:
                    result['标题'] = meta[3]
                if '电视节目标题' in result:
                    result['电视节目标题'] = meta[3]
                if '集标题' in result:
                    result['集标题'] = meta[3]
        except Exception as e:
            pass
        # try:
        #     json_ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',res.text,re.S).group(1))
        #
        #     if '标题' in result:
        #         result['标题'] = json_ld.get('name')
        #     if '电视节目标题' in result:
        #         result['电视节目标题'] = json_ld.get('name')
        #     if '集标题' in result:
        #         result['集标题'] = json_ld.get('name')
        #
        #
        #
        #     result['级别'] = 'R18+'
        #     result['评级'] = self.format_rate_str(json_ld.get('aggregateRating').get('ratingValue'))
        #
        #     result['tag']['type'] = stype
        #     result['tag']['dital_url'] = res.url
        #     result['tag']['video_id'] = re.search(r'cid=(.+)/', res.url).group(1)
        #
        #     result['tag']['backdrop'] = utils.tim_img_bytes(self.download_page_request(self.get_full_src(json_ld.get('image'))).content)
        #     result['tag']['poster'] = utils.create_poster(result['tag']['backdrop'])
        #     result['tag']['total'] = 0
        #     result['tag']['tip'] = ''
        #
        #
        #
        # except Exception:
        #         pass
        #
        #
        # result['dital_url'] = res.url

        return result

    def search(self, keyword, stype):
        if keyword.startswith('http'):
            res = self.download_page_request(keyword)

            yield self.parse_url_search(res, stype)
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
                        print('搜索失败')
                        # sleep(0.1)

    def dital(self, url, meta):

        res = self.download_page_request(url)
        if res:
            return self.parse_dital(res.text, meta)

    def parse_dital(self, html, meta):  #todo ﻿http://www.data18.com/movies/154497 无法抓取 ﻿http://www.data18.com/movies/154574
        if not html or not meta: return
        soup = BeautifulSoup(html, "lxml")

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
            year = re.search(r'Release date: (.*?\d{4})', year).group(1)
            if '发布日期' in meta:
                meta['发布日期'] = utils.format_date_str(year)
            if '发布日期(电视节目)' in meta:
                meta['发布日期(电视节目)'] = utils.format_date_str(year)
            if '发布日期(集)' in meta:
                meta['发布日期(集)'] = utils.format_date_str(year)
            try:
                meta['摘要'] = div_main.select_one('div.gen12 > p.gen12').text.strip().strip('Description:')
                meta['标语'] = meta['摘要'][:30]
            except Exception:
                pass

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

        # pa = re.search(r'<meta name="keywords".*?content="(.*?)".*'
        #                r'<a href="(.*?)" class="grouped_elements" rel="covers".*?'
        #                r'Click Cover to Enlarge - <a href="(.*?)".*?'
        #                r'<p>Production Year.*?Release date: (.*?\d{4}).*?</p>.*?'
        #                r'<b>Site:</b> <a href=".*?">(.*?)</a> \| '
        #                r'<b>Director:</b> (.*?)</p>.*?'
        #                r'<b>Categories:</b>(.*?)</p>.*?'
        #                r'<b>Description:</b><br />(.*?)</p></div>.*?'
        #                r'<div class="contenedor"(.*?)</p><.*?/div>.*?</div>', html, re.S)
        #
        # if not pa.groups():
        #     pa = re.search(r'<meta name="keywords".*?content="(.*?)".*'
        #                    r'<a href="(.*?)" class="grouped_elements" rel="covers".*?'
        #                    r'Click to Enlarge Front & Back Cover.*?'
        #                    r'<p>Production Year.*?Release date: (.*?\d{4}).*?</p>.*?'
        #                    r'<b>Site:</b> <a href=".*?">(.*?)</a> \| '
        #                    r'<b>Director:</b> (.*?)</p>.*?'
        #                    r'<b>Categories:</b>(.*?)</p>.*?'
        #                    r'<b>Description:</b><br />(.*?)</p></div>.*?'
        #                    r'<div class="contenedor"(.*?)</p><.*?/div>.*?</div>', html, re.S)
        #
        # geres = []
        # geres_a = re.findall(r'<a href=".*?">(.*?)</a>', pa.group(7), re.S)
        # if geres_a:
        #     geres.extend(geres_a)
        # geres_b = re.findall(r'<span class="gensmall">(.*?)</span>', pa.group(7), re.S)
        # if geres_b:
        #     geres.extend(geres_b)
        #
        # if '标题' in meta:
        #     meta['标题'] = pa.group(1)
        # if '电视节目标题' in meta:
        #     meta['电视节目标题'] = pa.group(1)
        # if '集标题' in meta:
        #     meta['集标题'] = pa.group(1)
        #
        # if '发布日期' in meta:
        #     meta['发布日期'] = utils.format_date_str(pa.group(4))
        # if '发布日期(电视节目)' in meta:
        #     meta['发布日期(电视节目)'] = utils.format_date_str(pa.group(4))
        # if '发布日期(集)' in meta:
        #     meta['发布日期(集)'] = utils.format_date_str(pa.group(4))
        #
        # meta['级别'] = 'R18+'
        #
        # meta['摘要'] = pa.group(8).strip()
        # meta['标语'] = meta['摘要'][:30]
        #
        # geres = [a for a in filter(lambda x: x.find(':') < 0, geres)]
        # meta['类型'] = ','.join(geres)
        #
        # actors = re.findall(r'<a href=".*?" class="gensmall">(.*?)</a>', pa.group(9), re.S)
        # meta['演员'] = ','.join(actors)
        #
        # meta['导演'] = ','.join([pa.group(6)])
        #
        # meta['作者'] = ','.join([pa.group(5)])
        #
        # meta['tag']['poster'] = utils.tim_img_bytes(self.download_page_request(pa.group(2)).content)
        # meta['tag']['backdrop'] = utils.tim_img_bytes(self.download_page_request(pa.group(3)).content)
        #
        #
        # yield meta

        # # 缩略图
        # samples = re.findall(r'src="(https?://pics.dmm.co.jp/.+?-\d{1,2}.jpg)"', html)
        # if samples:
        #     for sample in samples:
        #         url = self.get_full_src(sample)
        #         yield self.download_page_request(url).content
