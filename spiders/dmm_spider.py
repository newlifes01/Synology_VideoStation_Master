#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from time import sleep
from urllib.parse import urljoin

import re
from bs4 import BeautifulSoup

import utils
from spiders.base_spider import BaseSpider


class DmmSpider(BaseSpider):
    def format_rate_str(self, rate_str):
        try:
            return str(round((float(rate_str.strip()) * 20)))
        except:
            return '0'

    def get_full_src(self, src):
        search = re.search(r'(p[a-z]\.)jpg', src)
        if search:
            return src.replace(search.group(1), 'pl.')

        search = re.search(r'consumer_game', src)
        if search:
            return src.replace('js-', '-')

        search = re.search(r'js\-([0-9]+)\.jpg$', src)
        if search:
            return src.replace('js-', 'jp-')

        search = re.search(r'ts\-([0-9]+)\.jpg$', src)
        if search:
            return src.replace('ts-', 'tl-')

        search = re.search(r'(\-[0-9]+\.)jpg$', src)
        if search:
            return src.replace(search.group(1), 'jp' + search.group(1))

        return src.replace('-', 'jp-')

    def get_url_type(self, url):
        if re.match(r'https?://www.dmm.co.jp/digital/anime/-/detail/=/cid=', url):
            return 0
        elif re.match(r'https?://www.dmm.co.jp/digital/videoa/-/detail/=/cid=', url):
            return 1
        elif re.match(r'https?://www.dmm.co.jp/mono/anime/-/detail/=/cid=', url):
            return 2
        elif re.match(r'https?://www.dmm.co.jp/mono/dvd/-/detail/=/cid=', url):
            return 3
        elif re.match(r'https?://www.dmm.co.jp/mono/vhs/-/detail/=/cid=', url):
            return -1
        elif re.match(r'https?://www.dmm.co.jp/monthly/avstation/-/detail/=/cid=', url):
            return 5
        elif re.match(r'https?://www.dmm.co.jp/monthly/playgirl/-/detail/=/cid=', url):
            return 6
        elif re.match(r'https?://www.dmm.co.jp/monthly/premium/-/detail/=/cid=', url):
            return 7
        elif re.match(r'https?://www.dmm.co.jp/monthly/prime/-/detail/=/cid=', url):
            return 8
        elif re.match(r'https?://www.dmm.co.jp/ppm/video/-/detail/=/cid=', url):
            return 9
        elif re.match(r'https?://www.dmm.co.jp/rental/-/detail/=/cid=', url):
            return 10
        elif re.match(r'https?://www.dmm.co.jp/rental/ppr/-/detail/=/cid=', url):
            return 11
        else:
            return -1

    def parse_search_html(self, res,stype):
        if not res:
            return
        next_page = re.search(r'<li><a href="(http://www.dmm.co.jp/.+?page=\d*)/">次へ</a>'
                              , res.text, re.IGNORECASE)
        if next_page:
            url = next_page.group(1)
            self.add_urls(url)

        soup = BeautifulSoup(res.text, 'lxml')
        total = soup.select_one('div.list-boxcaptside.list-boxpagenation > p')
        li_nodes = soup.select("#list li")

        for li in li_nodes:
            if self.stoped:
                break
            sell = li.select_one('p.sublink a')
            url = li.select_one('p.tmb a').get('href')
            url_type = self.get_url_type(url)
            if url_type >= 0:
                src_url = 'http:' + li.select_one('p.tmb a img').get('src')
                result = utils.gen_metadata_struck(stype)
                if '标题' in result:
                    result['标题'] = li.select_one('p.tmb a img').get('alt')
                if '电视节目标题' in result:
                    result['电视节目标题'] = li.select_one('p.tmb a img').get('alt')
                if '集标题' in result:
                    result['集标题'] = li.select_one('p.tmb a img').get('alt')
                result['级别'] = 'R18+'
                try:
                    result['评级'] = self.format_rate_str(li.select_one('div.value p.rate').text)
                except Exception:
                    pass

                result['tag']['type'] = stype
                result['tag']['dital_url'] = url
                result['tag']['video_id'] = re.search(r'cid=(.+)/', url).group(1)

                result['tag']['backdrop'] = utils.tim_img_bytes(self.download_page_request(self.get_full_src(src_url)).content)
                result['tag']['poster'] = utils.create_poster(result['tag']['backdrop'])
                result['tag']['total'] = int(re.match(r'(\d+).*', total.get_text()).group(1)) if total else 0
                result['tag']['tip'] = sell.get_text() if sell else ''

                yield result


                # result = utils.get_spider_metastruct()
                #
                # result['标题'] = li.select_one('p.tmb a img').get('alt')
                # result['电视节目标题'] = result['标题']
                # result['集标题'] = result['标题']
                #
                # result['级别'] = 'R18+'
                # try:
                #     result['评级'] = self.format_rate_str(li.select_one('div.value p.rate').text)
                # except Exception:
                #     pass
                #
                # result['dital_url'] = url
                # result['id'] = re.search(r'cid=(.+)/', url).group(1)
                #
                # result['backdrop'] = utils.tim_img_bytes(self.download_page_request(self.get_full_src(src_url)).content)
                # result['poster'] = utils.create_poster(result['backdrop'])
                # result['total'] = int(re.match(r'(\d+).*', total.get_text()).group(1)) if total else 0
                # result['tip'] = sell.get_text() if sell else ''
                #
                #
                # yield result

    def parse_url_search(self, res ,stype='movie'):
        if not res:
            return
        result = utils.gen_metadata_struck(stype)
        try:
            json_ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',res.text,re.S).group(1))

            if '标题' in result:
                result['标题'] = json_ld.get('name')
            if '电视节目标题' in result:
                result['电视节目标题'] = json_ld.get('name')
            if '集标题' in result:
                result['集标题'] = json_ld.get('name')



            result['级别'] = 'R18+'
            result['评级'] = self.format_rate_str(json_ld.get('aggregateRating').get('ratingValue'))

            result['tag']['type'] = stype
            result['tag']['dital_url'] = res.url
            result['tag']['video_id'] = re.search(r'cid=(.+)/', res.url).group(1)

            result['tag']['backdrop'] = utils.tim_img_bytes(self.download_page_request(self.get_full_src(json_ld.get('image'))).content)
            result['tag']['poster'] = utils.create_poster(result['tag']['backdrop'])
            result['tag']['total'] = 0
            result['tag']['tip'] = ''



        except Exception:
                pass


        result['dital_url'] = res.url

        return result

    def search(self, keyword,stype):
        if keyword.startswith('http'):
            res = self.download_page_request(keyword, True)

            yield self.parse_url_search(res,stype)
        else:
            self.add_urls('http://www.dmm.co.jp/search/=/searchstr={}/limit=120/sort=date/'.format(keyword))
            while self.has_url():
                url = self.get_urls()
                if url:
                    res = self.download_page_request(url, True)
                    if res:
                        for each in self.parse_search_html(res,stype):
                            yield each
                    else:
                        print('搜索失败')
            sleep(0.1)

    def parse_dital(self, html, meta):
        if not html or not meta: return
        url_type = self.get_url_type(meta.get('tag').get('dital_url'))
        if url_type < 0: return
        # 年份
        try:
            if url_type in [2, 3]:
                year = re.search(r'発売日：.*?(\d{4}/\d{2}/\d{2})', html, re.S)
            elif url_type == 8:
                year = re.search(r'商品発売日.*?(\d{4}/\d{2}/\d{2})', html, re.S)
            elif url_type in [10, 11]:
                year = re.search(r'貸出開始日：.*?(\d{4}/\d{2}/\d{2})', html, re.S)
            else:  # 0,1,5,6,7,9
                year = re.search(r'配信開始日：.*?(\d{4}/\d{2}/\d{2})', html, re.S)


            if '发布日期' in meta:
                meta['发布日期'] = utils.format_date_str(year.group(1))
            if '发布日期(电视节目)' in meta:
                meta['发布日期(电视节目)'] = utils.format_date_str(year.group(1))
            if '发布日期(集)' in meta:
                meta['发布日期(集)'] = utils.format_date_str(year.group(1))
        except Exception:
            pass

        try:
            # 简介
            des = re.search('<meta\s*?property="og:description"\s*?content="(.+?)"\s*?/>', html)
            if not des:
                des = re.search('<meta\s*?name="description"\s*?content="(.+?)"\s*?>', html)
            meta['摘要'] = des.group(1).strip()
            meta['标语'] = meta['摘要'][:30]
        except Exception:
            pass

        lst_genre = []
        try:
            id_number = re.search(r'cid=(.+)/', meta.get('dital_url')).group(1)
            lst_genre.append(id_number)
        except Exception:
            pass

        try:
            # 专辑
            if url_type == 8:
                gen = re.search(r'<tr><th>レーベル</th><td>(.+?)</td></tr>', html)
            else:
                gen = re.search(r'<tr>\s*?<td.*?>レーベル：</td>\s*?<td.*?>(.+?)</td>\s*?</tr>', html, re.S)
            if gen:
                # lst_genre.append(gen.group(1))
                tmp = re.search('<a href=".+?">(.+?)</a>', gen.group(1))
                if tmp:
                    lst_genre.append(tmp.group(1))
                    # print(lst_genre)
        except Exception:
            pass

        try:
            # 分类
            if url_type == 8:
                album = re.search(r'<tr><th>シリーズ</th><td>(.+?)</td></tr>', html)
            else:
                album = re.search(r'<tr>\s*?<td.*?>シリーズ：</td>\s*?<td.*?>(.+?)</td>\s*?</tr>', html, re.S)

            if album:
                # lst_genre.append(album.group(1))
                tmp = re.search('<a href=".+?">(.+?)</a>', album.group(1))
                if tmp:
                    lst_genre.append(tmp.group(1))

        except Exception:
            pass

        try:
            # 标签
            if url_type == 8:
                cmt = re.search(r'<tr><th>ジャンル</th><td>(.+?)</td></tr>', html)
            else:
                cmt = re.search(r'<tr>\s*?<td.*?>ジャンル：</td>\s*?<td.*?>(.+?)</td>\s*?</tr>', html, re.S)
            if cmt:
                tags = re.findall(r'<a href=".+?">(.+?)</a>', cmt.group(1))
                if tags and len(tags) > 0:
                    lst_genre.extend(tags)
        except Exception:
            pass
        if lst_genre:
            meta['类型'] = ','.join(lst_genre)

        try:
            # 演员
            if url_type == 8:
                jst = re.search(r'\$\(\'\#fn-visibleActor\'\)\.visibleActor\(\{.*?'
                                r'url: \'(.+?)\'.*?'
                                r'\}\)\;', html, re.S)
            else:
                jst = re.search('\$\("a#a_performer"\).click\(function\(\) \{.*?'
                                '\$\.ajax\(\{.*?'
                                'type: "GET",.*?'
                                'url: \'(.+?)\',.*?'
                                , html, re.S)
            cast_node = None
            if jst:
                ajxurl = urljoin('http://www.dmm.co.jp/', jst.group(1))
                cast_node_res = self.download_page_request(ajxurl, True)
                cast_node_res.encoding = 'utf-8'
                cast_node = cast_node_res.text
            else:
                if url_type == 8:
                    tmp = re.search('<div class="info__boxActor fn-boxActor">(.+?)</div>', html, re.S)
                else:
                    tmp = re.search('<span id="performer">(.+?)</span>', html, re.S)
                if tmp:
                    cast_node = tmp.group(1)
            if cast_node:
                meta['演员'] = ','.join(re.findall('<a href="/.+/-/list/=/article=actress/id=\d+/">(.+?)</a>',
                                                 cast_node))

        except Exception:
            pass

        try:
            # 导演
            if url_type == 8:
                directors = re.search(r'<tr><th>監督</th><td>(.+?)</td></tr>', html)
            else:
                directors = re.search(r'<tr>\s*?<td.*?>監督：</td>\s*?<td.*?>(.+?)</td>\s*?</tr>', html, re.S)
            if directors:
                meta['导演'] = ','.join(directors.group(1).strip().split(' '))
                tmp = re.findall('<a href=".+?"\s*?>(.+?)</a>', directors.group(1))
                if tmp and len(tmp):
                    meta['导演'] = ','.join(tmp)
        except Exception:
            pass

        try:
            # 制片商
            if url_type == 8:
                studio = re.search(r'<tr><th>メーカー</th><td>(.+?)</td></tr>', html)
            else:
                studio = re.search(r'<tr>\s*?<td.*?>メーカー：</td>\s*?<td.*?>(.+?)</td>\s*?</tr>', html, re.S)
            if studio:
                meta['作者'] = ','.join(studio.group(1).split(' '))
                tmp = re.findall('<a href=".+?">(.+?)</a>', studio.group(1))
                if tmp and len(tmp):
                    meta['作者'] = ','.join(tmp)


        except  Exception:
            pass

        return meta,[]

    def dital(self, url, meta):

        res = self.download_page_request(url, True)
        if res:
            return self.parse_dital(res.text, meta)


if __name__ == '__main__':
    dmm = DmmSpider('dmm')
    for each in dmm.search('iptd'):
        print(each)
