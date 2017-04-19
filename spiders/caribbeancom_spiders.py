#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: syaofox@gmail.com
import re
from urllib.parse import urljoin, quote

from pyquery import PyQuery

import utils
from spiders.base_spider import BaseSpider


class CaribbeancomSpider(BaseSpider):
    def parse_url_search(self, res, stype='movie'):
        if not res:
            return

        result = utils.gen_metadata_struck(stype)
        try:

            doc = PyQuery(res.text)
            # print(doc)

            title = doc('#main-content > div.main-content-movieinfo > div.video-detail > h1').text()

            if '标题' in result:
                result['标题'] = title
            if '电视节目标题' in result:
                result['电视节目标题'] = title
            if '集标题' in result:
                result['集标题'] = title

            result['级别'] = 'R18+'

            result['tag']['type'] = stype
            result['tag']['dital_url'] = res.url
            result['tag']['video_id'] = re.search(r'/(\d+-\d+)/index', result['tag']['dital_url']).group(1)
            result['tag']['tip'] = doc(
                '#main-content > div.main-content-movieinfo > div.movie-info > dl:nth-child(1) > dd > a > span').text()
            result['tag']['xy'] = (40, 30)

            poster_url = 'https://www.caribbeancom.com/moviepages/{}/images/l_l.jpg'.format(result['tag']['video_id'])
            if poster_url:
                result['tag']['poster'] = self.download_page_request(poster_url).content

        except Exception:
            pass

        return result

    def parse_search_html(self, res, stype):
        if not res:
            return
        res.encoding = 'euc-jp'
        html = res.text
        main_url = res.url
        doc = PyQuery(html)

        next_page = doc('a.go-to-next')
        if next_page.text() == '次へ':
            self.add_urls(urljoin(main_url, next_page.attr('href')))

        try:
            total = doc('#main-content > h1 > small').text()
            total = re.search('(\d+)', total).group(1)

            yield int(total)
        except Exception:
            pass

        divs = doc('#main-content > div.list-area > div').items()
        for div in divs:
            result = utils.gen_metadata_struck(stype)
            title = div('span.movie-title > a').text()
            if '标题' in result:
                result['标题'] = title
            if '电视节目标题' in result:
                result['电视节目标题'] = title
            if '集标题' in result:
                result['集标题'] = title
            result['级别'] = 'R18+'
            result['tag']['type'] = stype
            result['tag']['dital_url'] = urljoin(main_url, div('a').attr('href'))
            result['tag']['video_id'] = re.search(r'/(\d+-\d+)/index', result['tag']['dital_url']).group(1)
            result['tag']['tip'] = div('span.movie-actor > a > span').text()
            poster_url = div('a > img').attr('src')
            if poster_url:
                result['tag']['poster'] = self.download_page_request(poster_url).content
                result['tag']['xy'] = (40, 30)
            yield result

    def search(self, keyword, stype):
        mid = re.search(r'(\d{6}[_-]\d{3})', keyword)
        if mid:
            res = self.download_page_request('http://www.caribbeancom.com/moviepages/{}/index.html'.format(mid.group(1)))
            yield self.parse_url_search(res, stype)
        elif keyword.startswith('http'):
            res = self.download_page_request(keyword)
            yield self.parse_url_search(res, stype)
        else:
            self.add_urls(
                'http://www.caribbeancom.com/search/?q={}'.format(quote(keyword, encoding='euc-jp')))
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
            date = doc('#main-content > div.main-content-movieinfo > div.movie-info > dl:nth-child(3) > dd').text()
            if '发布日期' in meta:
                meta['发布日期'] = date
            if '发布日期(电视节目)' in meta:
                meta['发布日期(电视节目)'] = date
            if '发布日期(集)' in meta:
                meta['发布日期(集)'] = date
        except AttributeError:
            pass

        try:
            des = doc('#main-content > div.main-content-movieinfo > div.movie-comment > p').text()

            meta['摘要'] = des.strip()
            meta['标语'] = meta['摘要'][:30]
        except AttributeError:
            pass

        try:
            lst=[]
            genres = doc('#main-content > div.main-content-movieinfo > div.movie-info > dl.movie-info-cat > dd').items()
            if genres:
                lst= [genre.text().strip() for genre in genres]

            groups = doc('#main-content > div.main-content-movieinfo > div.movie-info > dl:nth-child(6) > dd').items()
            if groups:
                groups = [group.text().strip() for group in groups]
                lst.extend(groups)
            meta['类型'] = ','.join(lst)
        except AttributeError:
            pass

        try:
            actors = doc('#main-content > div.main-content-movieinfo > div.movie-info > dl:nth-child(1) > dd').items()
            meta['演员'] = ','.join([actor.text().strip() for actor in actors])
        except AttributeError:
            pass

        try:
            meta['作者'] = 'カリビアンコム'
        except AttributeError:
            pass

        try:
            starts = doc('#main-content > div.main-content-movieinfo > div.movie-info > dl:nth-child(5) > dd').text()
            if starts:

                meta['评级'] = str(20*len(starts))
        except AttributeError:
            pass

        try:
            poster_url = 'https://www.caribbeancom.com/moviepages/{}/images/l_l.jpg'.format(meta['tag']['video_id'])
            poster_data = self.download_page_request(poster_url).content
            meta['tag']['backdrop'] = utils.tim_img_bytes(poster_data)
            meta['tag']['poster'] = utils.create_poster(meta['tag']['backdrop'])
        except AttributeError:
            pass
        yield meta

        try:
            # 缩略图
            sample_urls = doc('a.fancy-gallery').items()
            for sample_url in sample_urls:
                nail_url = sample_url.attr('href')
                if nail_url:
                    nail_url = urljoin(meta.get('tag').get('dital_url'),nail_url)
                    if nail_url.find('member') < 0:
                        yield self.download_page_request(nail_url).content

        except Exception:
            pass

    def dital(self, url, meta):
        res = self.download_page_request(url)
        if res:
            return self.parse_dital(res.text, meta)


if __name__ == '__main__':
    test = CaribbeancomSpider('CaribbeancomSpider')
    for each in test.search('120916-001', 'movie'):
        print(each)
        if not isinstance(each,int):
            print(each.get('tag').get('dital_url'))
            for dital in test.dital(each.get('tag').get('dital_url'), each):
                print(dital)
            break
