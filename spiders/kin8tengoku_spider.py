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
            # print(doc)

            title = doc('head > title').text()

            if '标题' in result:
                result['标题'] = title
            if '电视节目标题' in result:
                result['电视节目标题'] = title
            if '集标题' in result:
                result['集标题'] = title

            result['级别'] = 'R18+'

            result['tag']['type'] = stype
            result['tag']['dital_url'] = res.url
            result['tag']['video_id'] = re.search(r'/(\d+)/index',result['tag']['dital_url']).group(1)
            result['tag']['tip'] = doc('#detail_box > table >tr:nth-child(1)  a').text()

            poster_url = re.search(r"var imgurl = '(http://.*?jpg)';",res.text,re.S).group(1)
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
                result['tag']['xy'] = (40,30)
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


    def parse_dital(self, html, meta):
        if not html or not meta: return
        doc = pq(html)

        try:
            date = doc('#detail_box > table > tr:nth-child(7) > td.movie_table_td2').text()
            if '发布日期' in meta:
                meta['发布日期'] = date
            if '发布日期(电视节目)' in meta:
                meta['发布日期(电视节目)'] = date
            if '发布日期(集)' in meta:
                meta['发布日期(集)'] = date
        except AttributeError:
            pass

        try:
            des = doc('#comment').text()

            meta['摘要'] = des.strip()
            meta['标语'] = meta['摘要'][:30]
        except AttributeError:
            pass

        try:

            genres = doc('#detail_box > table > tr:nth-child(5) > td.movie_table_td2 > div').items()
            meta['类型'] = ','.join([genre.text().strip() for genre in genres])
        except AttributeError:
            pass

        try:
            actors = doc('#detail_box > table >tr:nth-child(1) a').items()
            meta['演员'] = ','.join([actor.text().strip() for actor in actors])
        except AttributeError:
            pass

        # try:
        #     producers = doc('#titlebox > ul:nth-child(4) > li:nth-child(2) > a').items()
        #     meta['作者'] = ','.join([producer.text().strip() for producer in producers])
        # except AttributeError:
        #     pass

        try:
            poster_data = self.download_page_request(re.search(r"var imgurl = '(http://.*?jpg)';",html,re.S).group(1)).content
            meta['tag']['backdrop'] = utils.tim_img_bytes(poster_data)
            meta['tag']['poster'] = utils.create_poster(meta['tag']['backdrop'])
        except AttributeError:
            pass
        yield meta

        # try:
        #     # 缩略图
        #     sample_url = doc(
        #         '#TabbedPanels1 > div > div.TabbedPanelsContent.TabbedPanelsContentVisible > a > img').attr('src')
        #     yield self.download_page_request(sample_url).content
        #
        # except Exception:
        #     pass

    def dital(self, url, meta):
        res = self.download_page_request(url)
        if res:
            return self.parse_dital(res.text, meta)


if __name__ == '__main__':
    test = Kin8tengokuSpider('kin8')
    # for each in test.search('http://www.kin8tengoku.com/moviepages/0959/index.html','movie'):
    #     print(each)

    for each in test.dital('http://www.kin8tengoku.com/moviepages/0959/index.html',utils.gen_metadata_struck('movie')):
        print(each)