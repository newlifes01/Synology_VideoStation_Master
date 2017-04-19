#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: syaofox@gmail.com
import utils
from models.themoviedb_API import TheMovieDBAPI
from spiders.base_spider import BaseSpider


class ThemoviedbSpider(BaseSpider):
    tmdb_api = TheMovieDBAPI()

    def parse_search_html(self, keyword, stype):
        if not keyword:
            return

        movies = self.tmdb_api.search_movie(keyword, meth=stype)

        for movie in movies:
            url = movie['tag']['thumbnail_url']
            if url:
                movie['tag']['poster'] = utils.tim_img_bytes(
                    self.download_page_request(movie['tag']['thumbnail_url']).content)
            movie['tag']['video_id'] = str(movie['tag']['tmdb_id'])
            movie['tag']['tip'] = movie['类型']
            if '发布日期' in movie:
                movie['tag']['tip'] = movie['发布日期']
            if '发布日期(电视节目)' in movie:
                movie['tag']['tip'] = movie['发布日期(电视节目)']
            if '发布日期(集)' in movie:
                movie['tag']['tip'] = movie['发布日期(集)']

            yield movie

    def search(self, keyword, stype):
        if keyword.startswith('http'):

            yield self.parse_search_html(keyword, stype)
        else:
            for each in self.parse_search_html(keyword, stype):
                yield each

    def parse_dital(self, nid, meta):
        if not meta:
            return
        movie = self.tmdb_api.get_dital(meta['tag']['tmdb_id'], meth=meta['tag']['type'])
        if movie:

            url = movie['tag']['poster_url']
            if url:
                movie['tag']['poster'] = utils.tim_img_bytes(
                    self.download_page_request(movie['tag']['poster_url']).content)
            url = movie['tag']['backdrop_url']

            if url:
                movie['tag']['backdrop'] = utils.tim_img_bytes(
                    self.download_page_request(movie['tag']['backdrop_url']).content)
            yield movie
            try:
                # 缩略图
                samples = movie['tag']['img_urls']
                for sample in samples:
                    yield self.download_page_request(sample).content
            except Exception:
                pass

    def dital(self, url, meta):

        return self.parse_dital('', meta)
