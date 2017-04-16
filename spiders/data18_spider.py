#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: syaofox@gmail.com
import re

import utils
from spiders.base_spider import BaseSpider

class Data18Spider(BaseSpider):
    def parse_search_html(self, res,stype):
        if not res:
            return

        relock = re.search(r'<a href="(.*?)">Click here to continue\.\.\.</a>',res.text)
        if relock:
            self.download_page_request(relock.group(1))
            self.add_log('parse_search_html 重置:', relock.group(1))
            self.add_urls(relock.group(1),True)
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
        meta_movies = re.findall(pattern,res.text)
        if meta_movies:
            metas.extend(meta_movies)

        pattern2 = re.compile(r'<div class="bscene genmed".*?</b>(.*?\d{2}.*?\d{4}.*?)</p>.*?'
                              r'<p class="line1">.*?<a href="(http://.*?)">.*?'
                              r'<img src="(http://.*?)".*?'
                              r'title="(.*?)".*?'
                              r'.*?</div>',re.S)

        metas_contens = re.findall(pattern2, res.text)
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
                self.add_log('parse_search_html 抓取标题错误:',e,level='error')

            result['tag']['type'] = stype
            result['tag']['dital_url'] = meta[1].strip()
            result['tag']['video_id'] = re.search(r'/(\d+)', meta[1]).group(1)

            # result['tag']['backdrop'] = utils.tim_img_bytes(self.download_page_request(self.get_full_src(src_url)).content)
            result['tag']['poster'] = utils.tim_img_bytes(self.download_page_request(meta[2]).content)
            result['tag']['total'] = 0
            result['tag']['tip'] = utils.format_date_str(meta[0].strip())
            yield result




        # if not res:
        #     return
        # next_page = re.search(r'<li><a href="(http://www.dmm.co.jp/.+?page=\d*)/">次へ</a>'
        #                       , res.text, re.IGNORECASE)
        # if next_page:
        #     url = next_page.group(1)
        #     self.add_urls(url)
        #
        # soup = BeautifulSoup(res.text, 'lxml')
        # total = soup.select_one('div.list-boxcaptside.list-boxpagenation > p')
        # li_nodes = soup.select("#list li")
        #
        # for li in li_nodes:
        #     if self.stoped:
        #         break
        #     sell = li.select_one('p.sublink a')
        #     url = li.select_one('p.tmb a').get('href')
        #     url_type = self.get_url_type(url)
        #     if url_type >= 0:
        #         src_url = 'http:' + li.select_one('p.tmb a img').get('src')
        #         result = utils.gen_metadata_struck(stype)
        #         if '标题' in result:
        #             result['标题'] = li.select_one('p.tmb a img').get('alt')
        #         if '电视节目标题' in result:
        #             result['电视节目标题'] = li.select_one('p.tmb a img').get('alt')
        #         if '集标题' in result:
        #             result['集标题'] = li.select_one('p.tmb a img').get('alt')
        #         result['级别'] = 'R18+'
        #         try:
        #             result['评级'] = self.format_rate_str(li.select_one('div.value p.rate').text)
        #         except Exception:
        #             pass
        #
        #         result['tag']['type'] = stype
        #         result['tag']['dital_url'] = url
        #         result['tag']['video_id'] = re.search(r'cid=(.+)/', url).group(1)
        #
        #         result['tag']['backdrop'] = utils.tim_img_bytes(self.download_page_request(self.get_full_src(src_url)).content)
        #         result['tag']['poster'] = utils.create_poster(result['tag']['backdrop'])
        #         result['tag']['total'] = int(re.match(r'(\d+).*', total.get_text()).group(1)) if total else 0
        #         result['tag']['tip'] = sell.get_text() if sell else ''

                # yield None # result

    def parse_url_search(self, res ,stype='movie'):
        if not res:
            return
        result = utils.gen_metadata_struck(stype)
        pattern = re.compile(r'<div style="float: left;.*?(\d{4}-\d{2}-\d{2}.*?)'
                             r'<a href="(http://.*?)">.*?'
                             r'<img src="(http://.*?)" style=".*?'
                             r'title="(.*?)".*?')
        metas = re.findall(pattern,res.text,re.S)
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

    def search(self, keyword,stype):
        if keyword.startswith('http'):
            res = self.download_page_request(keyword)

            yield self.parse_url_search(res,stype)
        else:
            self.add_urls('http://www.data18.com/search/?k={}'.format(keyword))
            while self.has_url():
                url = self.get_urls()
                if url:
                    res = self.download_page_request(url)
                    if res:
                        for each in self.parse_search_html(res,stype):
                            yield each
                    else:
                        print('搜索失败')
            # sleep(0.1)