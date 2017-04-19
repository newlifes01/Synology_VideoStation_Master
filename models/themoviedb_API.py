#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: syaofox@gmail.com
import json
from time import sleep
from urllib.parse import quote, urljoin
import utils

import requests


class TheMovieDBAPI:
    def __init__(self):
        self.api_key = 'f919448806cc64110be65712943e341b'
        self.main_url = 'https://api.themoviedb.org/3'
        self.seasion = requests.session()

        self.config = {}
        self.get_configuration()

    def get_configuration(self):
        url = '{}/configuration?api_key={}'.format(self.main_url, self.api_key)
        sleep(0.5)
        res = self.seasion.get(url)
        if res.status_code == 200:
            config = json.loads(res.text).get('images')
            self.config['base_url'] = config.get('secure_base_url')
            self.config['thumbnail_size'] = config.get('poster_sizes')[0]
            self.config['poster_size'] = config.get('poster_sizes')[-1]
            self.config['backdrop_size'] = config.get('backdrop_sizes')[-1]

    def get_original_url(self, path):
        return '{}/{}/{}'.format(self.config['base_url'], self.config['poster_size'], path)

    def search_movie(self, keyword, language='', meth='movie'):
        '''
        
        
        :param keyword: 关键字
        :param include_adult: 成人内存
        :param language: 语言
        :param meth: 方法
        :return: 
                {
                  "page": 1,
                  "results": [
                    {
                      "poster_path": "/54eqz6OFHORtSH30L0gedCOIfBj.jpg",
                      "adult": false,
                      "overview": "Warriors called \"Saints\" are the champions of hope who have always appeared since the Age of Myth whenever evil threatens the world. In this present day story, many years since the long fought \"Holy War\" we find Saori Kido, a girl troubled by her mysterious powers. She is saved by a boy, Seiya \"Bronze Saint\" from a sudden attack by an assassin, through the accident Saori realizes her destiny and mission and decides to go to \"Sanctuary\" with Seiya and his company of Bronze Saints. In Sanctuary they confront \"Pope\" and wage a desperate battle against the greatest Saints, the \"Gold Saints\".",
                      "release_date": "2014-06-21",
                      "genre_ids": [
                        28,
                        16,
                        14
                      ],
                      "id": 287590,
                      "original_title": "聖闘士星矢 LEGEND of SANCTUARY",
                      "original_language": "ja",
                      "title": "Saint Seiya: Legend of Sanctuary",
                      "backdrop_path": "/kwlM5NAdNSkePzPzDIgijhWAHCI.jpg",
                      "popularity": 1.743757,
                      "vote_count": 132,
                      "video": false,
                      "vote_average": 5
                    }
                  ],
                  "total_results": 2,
                  "total_pages": 1
                }
        '''
        url = '{}/{}/{}'.format(self.main_url, 'search', meth)
        param = {
            'api_key': self.api_key,
            'language': language,
            'query': keyword,
            'include_adult': 'true',
        }

        res = self.seasion.get(url, params=param)
        sleep(0.5)
        if res.status_code == 200:
            print(res.text)
            results = json.loads(res.text).get('results')
            for result in results:

                meta = utils.gen_metadata_struck(meth)
                meta['tag']['total'] = len(result)
                title = result.get('original_title')
                if '标题' in meta:
                    meta['标题'] = title
                if '电视节目标题' in meta:
                    meta['电视节目标题'] = title
                if '集标题' in meta:
                    meta['集标题'] = title

                date = result.get('release_date')
                if '发布日期' in meta:
                    meta['发布日期'] = date
                if '发布日期(电视节目)' in meta:
                    meta['发布日期(电视节目)'] = date
                if '发布日期(集)' in meta:
                    meta['发布日期(集)'] = date

                meta['评级'] = str(round((result['vote_average'] * 10)))
                meta['标语'] = result['original_title']
                meta['摘要'] = result['overview']
                if result['poster_path']:
                    poster_url = self.get_original_url(result['poster_path'])
                    meta['tag']['poster_url'] = poster_url
                    thumbnail_url = '{}/{}/{}'.format(self.config['base_url'], self.config['thumbnail_size'],
                                                      result['poster_path'])
                    meta['tag']['thumbnail_url'] = thumbnail_url

                if result['backdrop_path']:
                    backdrop_url = self.get_original_url(result['backdrop_path'])
                    meta['tag']['backdrop_url'] = backdrop_url

                meta['tag']['tmdb_id'] = result['id']
                meta['tag']['type'] = meth


                yield meta

    def get_dital(self, id, meth='movie'):
        url = '{}/{}/{}'.format(self.main_url, meth, id)
        param = {
            'api_key': self.api_key,
            'append_to_response': 'images,keywords,credits',
        }

        res = self.seasion.get(url, params=param)
        sleep(0.5)
        if res.status_code == 200:
            meta = utils.gen_metadata_struck(meth)
            result = json.loads(res.text)
            title = result.get('original_title')
            if '标题' in meta:
                meta['标题'] = title
            if '电视节目标题' in meta:
                meta['电视节目标题'] = title
            if '集标题' in meta:
                meta['集标题'] = title

            date = result.get('release_date')
            if '发布日期' in meta:
                meta['发布日期'] = date
            if '发布日期(电视节目)' in meta:
                meta['发布日期(电视节目)'] = date
            if '发布日期(集)' in meta:
                meta['发布日期(集)'] = date

            meta['评级'] = str(round((result['vote_average'] * 10)))
            meta['标语'] = result['tagline']
            meta['摘要'] = result['overview']
            if result['adult']:
                meta['级别'] = 'R18+'
            if result['poster_path']:
                poster_url = self.get_original_url(result['poster_path'])
                meta['tag']['poster_url'] = poster_url
                thumbnail_url = '{}/{}/{}'.format(self.config['base_url'], self.config['thumbnail_size'],
                                                  result['poster_path'])
                meta['tag']['thumbnail_url'] = thumbnail_url

            if result['backdrop_path']:
                backdrop_url = self.get_original_url(result['backdrop_path'])
                meta['tag']['backdrop_url'] = backdrop_url

            lst_gener = []
            lst_gener.extend([x.get('name') for x in result['spoken_languages']])
            for genre in result['genres']:
                lst_gener.append(genre['name'] if genre['name'] else None)
            lst_gener.extend([x.get('name') for x in result['keywords']['keywords']])
            meta['类型'] = ','.join(lst_gener)

            meta['演员'] = ','.join([x.get('name') for x in result['credits']['cast']])

            crews = result['credits']['crew']
            lst_producers = []
            lst_directors = []
            for crew in crews:

                job = crew.get('job')
                name = crew.get('name')
                if job == 'Director' or job == 'Writer':
                    lst_directors.append(name)
                if job == 'Producer':
                    lst_producers.append(name)
            meta['作者'] = ','.join(lst_producers)
            meta['导演'] = ','.join(lst_producers)

            meta['tag']['tmdb_id'] = result['id']
            for x in result['images']['posters']:
                meta['tag']['img_urls'].append(self.get_original_url(x.get('file_path')))

            for x in result['images']['backdrops']:
                meta['tag']['img_urls'].append(self.get_original_url(x.get('file_path')))
            meta['tag']['type'] = meth

            return meta


if __name__ == '__main__':
    x = []
    x.append(None)
    mdb = TheMovieDBAPI()
    # print(mdb.config)
    # movies = mdb.search_movie('Pirates II: Stagnetti\'s Revenge ',meth='movie')
    # print(movies)
    # for each in movies:
    #     print(each)
    print(mdb.get_dital(14312))
