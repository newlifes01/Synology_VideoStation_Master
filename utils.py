#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from time import mktime, strptime

import os
import re
import requests
from PIL import Image, ImageChops
from PyQt5.QtCore import QFile

# 日志登记
from bs4 import BeautifulSoup
from io import BytesIO
from collections import OrderedDict

logging.basicConfig(level=logging.DEBUG)
# 下载最大重试次数
RETRYMAX = 5
# 下载超时时间
DOWN_TIME_OUT = 5
# 爬虫下载间隔
SPIDER_DOWNLOAD_SLEEP_TIME = 0.1

# 项目根目录
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
# 临时目录
CACHE_PATH = os.path.join(PROJECT_PATH, '.cache')
# 缓存文件路径
DSM_CACHE_PATH = os.path.join(PROJECT_PATH, 'http_cache.sqlite')

# 爬虫缓存保留时间 秒
SPIDER_CACHE_KEEP_TIME = 3600 * 24
# 缓存保留时间 秒
CACHE_KEEP_TIME = 10 * 60
# 表格宽高
ITEM_WIDTH, ITEM_HEIGHT = 30, 40  # 120, 180
HOMEVIEDO_WIDTH, HOMEVIDEO_HEIGHT = 40, 30  # 180, 100
# http服务端口
HTTP_SERVER_PORT = 8000
# 临时海报,背景路径
POSTER_FILE = 'poster.jpg'
BACKDROP_FILE = 'backdrop.jpg'
POSTER_PATH = os.path.join(CACHE_PATH, POSTER_FILE)
BACKDROP_PATH = os.path.join(CACHE_PATH, BACKDROP_FILE)

if not os.path.exists(CACHE_PATH):
    os.mkdir(CACHE_PATH)


def fill_cn_form_en(stype, cn, en):
    for k, v in cn.items():
        if k == 'tag':
            try:
                tag = cn[k]
                tag['type'] = stype
                tag['API'] = get_library_API(stype)
                tag['json_head'] = get_dsm_json_head(stype)
                tag['id'] = en.get('id')
                tag['library_id'] = en.get('library_id')
                tag['mapper_id'] = en.get('mapper_id')
                tag['poster_mtime'] = en.get('additional').get('poster_mtime')
                tag['backdrop_mtime'] = en.get('additional').get('backdrop_mtime')

            except Exception:
                pass

        if k == '文件名':
            try:
                cn[k] = os.path.basename(en.get('additional').get('file')[0].get('sharepath'))
            except Exception:
                pass

        if k == '标题' or k == '电视节目标题':
            try:
                cn[k] = en.get('title')
            except Exception:
                pass

        if k == '标语' or k == '集标题':
            try:
                cn[k] = en.get('tagline')
            except Exception:
                pass

        if k == '发布日期' or k == '发布日期(集)':
            try:
                cn[k] = en.get('original_available')
            except Exception:
                pass

        if k == '发布日期(电视节目)':
            try:
                cn[k] = en.get('tvshow_original_available')
            except Exception:
                pass

        if k == '录制开始时间':
            try:
                cn[k] = en.get('record_date')
            except Exception:
                pass

        if k == '季':
            try:
                cn[k] = str(en.get('season'))
            except Exception:
                pass
        if k == '季数':
            try:
                cn[k] = str(en.get('additional').get('total_seasons'))
            except Exception:
                pass

        if k == '集':
            try:
                cn[k] = str(en.get('episode'))
            except Exception:
                pass

        if k == '级别':
            try:
                cn[k] = str(en.get('certificate'))
            except Exception:
                pass

        if k == '评级':
            try:
                cn[k] = '{}'.format(en.get('rating'))
            except Exception:
                pass

        if k == '类型':
            try:
                cn[k] = ','.join(en.get('additional').get('genre', []))
            except Exception:
                pass

        if k == '演员':
            try:
                cn[k] = ','.join(en.get('additional').get('actor', []))
            except Exception:
                pass

        if k == '作者':
            try:
                cn[k] = ','.join(en.get('additional').get('writer', []))
            except Exception:
                pass

        if k == '导演':
            try:
                cn[k] = ','.join(en.get('additional').get('director', []))
            except Exception:
                pass

        if k == '摘要':
            try:
                cn[k] = en.get('additional').get('summary')
            except Exception:
                pass

    return OrderedDict(cn)


def gen_metadata_struck(kind):
    tag = {
        'tag': {
            'type': '',
            'API': '',
            'json_head': '',

            'id': '',
            'library_id': '',
            'mapper_id': '',

            'poster_mtime': '',
            'backdrop_mtime': '',
            'poster': b'',
            'backdrop': b'',

        }
    }
    struck = {
        'movie': {
            '文件名': '',
            '标题': '',
            '标语': '',

            '发布日期': '',
            '级别': '',
            '评级': '',
            '类型': '',
            '演员': '',
            '作者': '',
            '导演': '',
            '摘要': '',
        },
        'tvshow': {
            '电视节目标题': '',
            '发布日期': '',
            '摘要': '',
            '季数': '',
        },
        'tvshow_episode': {
            '文件名': '',
            '电视节目标题': '',
            '发布日期(电视节目)': '',
            '集标题': '',
            '季': '',
            '集': '',
            '发布日期(集)': '',
            '级别': '',
            '评级': '',
            '类型': '',
            '演员': '',
            '作者': '',
            '导演': '',
            '摘要': '',
        },
        'home_video': {
            '文件名': '',
            '标题': '',
            '录制开始时间': '',
            '级别': '',
            '评级': '',
            '类型': '',
            '演员': '',
            '作者': '',
            '导演': '',
            '摘要': '',
        }
    }
    result = struck.get(kind)
    result.update(tag)
    return OrderedDict(result)


def search_result_to_table_data(meta, stype):
    if not meta or not stype:
        return
    video_meta = None
    if stype == 'tvshow_episode':
        video_meta = get_dital_episode_struck()

        video_meta['poster'] = meta.get('poster')

        video_meta['电视节目标题'] = meta.get('电视节目标题')
        video_meta['发布日期(电视节目)'] = meta.get('电视节目标题')
        video_meta['集标题'] = meta.get('电视节目标题')
        video_meta['季'] = meta.get('电视节目标题')
        video_meta['集'] = meta.get('电视节目标题')
        video_meta['发布日期(集)'] = meta.get('电视节目标题')
        video_meta['级别'] = meta.get('级别')
        video_meta['类型'] = meta.get('类型')
        video_meta['评级'] = meta.get('评级')
        video_meta['演员'] = meta.get('演员')
        video_meta['作者'] = meta.get('作者')
        video_meta['导演'] = meta.get('导演')
        video_meta['摘要'] = meta.get('摘要')

    if stype == 'tvshow':
        video_meta = get_dital_tvshow_struck()

        video_meta['poster'] = meta.get('poster')

        video_meta['backdrop'] = meta.get('backdrop')

        video_meta['电视节目标题'] = meta.get('电视节目标题')
        video_meta['发布日期'] = meta.get('发布日期')

        video_meta['摘要'] = meta.get('摘要')
        video_meta['季数'] = meta.get('季数')

    if stype == 'movie':
        video_meta = get_dital_movie_struck()
        video_meta['poster'] = meta.get('poster')

        video_meta['backdrop'] = meta.get('backdrop')

        video_meta['标题'] = meta.get('标题')
        video_meta['标语'] = meta.get('标语')

        video_meta['发布日期'] = meta.get('发布日期')
        video_meta['级别'] = meta.get('级别')
        video_meta['评级'] = meta.get('评级')
        video_meta['类型'] = meta.get('类型')
        video_meta['演员'] = meta.get('演员')
        video_meta['作者'] = meta.get('作者')
        video_meta['导演'] = meta.get('导演')
        video_meta['摘要'] = meta.get('摘要')

    if stype == 'home_video':
        video_meta = get_dital_homevideo_struck()
        video_meta['poster'] = meta.get('poster')

        video_meta['backdrop'] = meta.get('backdrop')

        video_meta['标题'] = meta.get('标题')

        video_meta['录制开始时间'] = meta.get('录制开始时间')

        video_meta['级别'] = meta.get('级别')
        video_meta['评级'] = meta.get('评级')
        video_meta['类型'] = meta.get('类型')
        video_meta['演员'] = meta.get('演员')
        video_meta['作者'] = meta.get('作者')
        video_meta['导演'] = meta.get('导演')
        video_meta['摘要'] = meta.get('摘要')

    return video_meta


def seconds_to_struct(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if int(h) == 0 and int(m) == 0:
        return "%02d秒" % (s)

    elif int(h) == 0:
        return "%02d分%02d秒" % (m, s)
    else:
        return "%02d时%02d分%02d秒" % (h, m, s)


def format_time_stamp(timestr):
    try:
        a = strptime(timestr, '%Y-%m-%d %H:%M:%S.%f')
        return mktime(a)
    except Exception:
        pass

    try:
        return mktime(strptime(timestr, '%Y-%m-%d %H:%M:%S'))
    except Exception:
        pass

    try:
        return mktime(strptime(timestr, '%a, %d %b %Y %H:%M:%S %Z'))
    except Exception:
        pass




def add_log(loger, level, *msg):
    if not loger or not len(msg):
        return
    f_s = ' '
    for each in msg:
        f_s = f_s + ' {}'.format(each)
    f_s = f_s.strip()
    if level == 'debug':
        loger.debug(f_s)
    if level == 'info':
        loger.info(f_s)
    elif level == 'warn':
        loger.warn(f_s)
    elif level == 'error':
        loger.error(f_s)
    else:
        loger.critical(f_s)


def get_library_API(stype):
    if stype == 'movie':
        return 'Movie'
    if stype == 'tvshow':
        return 'TVShow'
    if stype == 'home_video':
        return 'HomeVideo'
    if stype == 'tvshow_episode':
        return 'TVShowEpisode'


def get_dsm_json_head(stype):
    if stype == 'movie':
        return 'movie'
    if stype == 'tvshow':
        return 'tvshow'
    if stype == 'home_video':
        return 'video'
    if stype == 'tvshow_episode':
        return 'episode'


def get_dital_tvshow_struck():
    return {
        '电视节目标题': '',
        '发布日期': '',
        '摘要': '',
        '季数': '',

        'poster': b'',
        'backdrop': b'',
    }


def get_dital_episode_struck():
    return {
        '文件名': '',
        '电视节目标题': '',
        '发布日期(电视节目)': '',
        '集标题': '',
        '季': '',
        '集': '',
        '发布日期(集)': '',
        '级别': '',
        '评级': '',
        '类型': '',
        '演员': '',
        '作者': '',
        '导演': '',
        '摘要': '',

        'poster': b'',

    }


def get_dital_movie_struck():
    return {
        '文件名': '',
        '标题': '',
        '标语': '',

        '发布日期': '',
        '级别': '',
        '评级': '',
        '类型': '',
        '演员': '',
        '作者': '',
        '导演': '',
        '摘要': '',

        'poster': b'',
        'backdrop': b'',
    }


def get_dital_homevideo_struck():
    return {
        '文件名': '',
        '标题': '',
        '录制开始时间': '',
        # '时间': '',
        '级别': '',
        '评级': '',
        '类型': '',
        '演员': '',
        '作者': '',
        '导演': '',
        '摘要': '',

        'poster': b'',
    }


def get_rating_lst():
    return [
        {'🎬PG': 'PG'},
        {'🎬PG12': 'PG12'},
        {'🎬R15+': 'R15+'},
        {'🎬R18+': 'R18+'},

        # {'🇺🇸G': 'G'},
        # {'🇺🇸PG': 'PG'},
        # {'🇺🇸PG-13': 'PG-13'},
        # {'🇺🇸R': 'R'},
        # {'🇺🇸NC-17': 'NC-17'},

        {'🎬Unrated': 'Unrated'},
    ]


def get_cert_idx(cert):
    data = {
        'PG': 0,
        'PG12': 1,
        'R15+': 2,
        'R18+': 3,
        'Unrated': 4,
    }
    return data.get(cert, -1)


def get_cert_txt(idx):
    data = {
        0: 'PG',
        1: 'PG12',
        2: 'R15+',
        3: 'R18+',
        4: 'Unrated',
    }
    return data.get(idx, 'Unrated')


def gen_liststr(list_str):
    if not list_str:
        return '[""]'
    list_str = re.sub(r'([,，]+)', ',', list_str.strip())
    list = list_str.split(',')

    if list and len(list):
        result_str = '['
        for each in list:
            result_str = result_str + '"{}"'.format(each) + ','

        if result_str.endswith(','):
            result_str = result_str[:-1]
        result_str = result_str + ']'

        return result_str

    return '[""]'


def get_screen_width(input_str, max_width=None, tail='.', tail_length=2):
    WIDTHS = [
        (126, 1), (159, 0), (687, 1), (710, 0), (711, 1),
        (727, 0), (733, 1), (879, 0), (1154, 1), (1161, 0),
        (4347, 1), (4447, 2), (7467, 1), (7521, 0), (8369, 1),
        (8426, 0), (9000, 1), (9002, 2), (11021, 1), (12350, 2),
        (12351, 1), (12438, 2), (12442, 0), (19893, 2), (19967, 1),
        (55203, 2), (63743, 1), (64106, 2), (65039, 1), (65059, 0),
        (65131, 2), (65279, 1), (65376, 2), (65500, 1), (65510, 2),
        (120831, 1), (262141, 2), (1114109, 1),
    ]
    """
    获取输入字符串input_str在屏幕上的显示宽度，全角字符宽度计算为2，半角字符宽度计算为1
    注意这个宽度并不能保证字符串能在屏幕上完美对齐，因为字体的原因，全角字符的宽度并不一定是半角字符的2倍
    如果仅需要获取字符串的宽度，只需提供input_str参数即可
    如果需要截取字符串，需提供最大截取宽度(max_width)和省略替代符号(tail, 可选)及其最大个数(tail_length, 可选)
    例如，最大截取宽度(max_width)为3,输入的字符串为 u"测试字符串"(长度为10)
    那截取结果是:
    u"..."
    如果截取宽度为4，那结果是:
    u"测.."(会自动少用一个表示省略的字符)
    如果截取宽度为5，那结果是:
    u"测..."
    """

    def get_char_width(char):
        """
        查表(WIDTHS)获取单个字符的宽度
        """
        char = ord(char)
        if char == 0xe or char == 0xf:
            return 0

        for num, wid in WIDTHS:
            if char < num:
                return wid

        return 1

    if max_width and max_width > tail_length * get_char_width(tail):
        # 最大宽度应该至少和表示省略的字符串一样长
        # str_max_width和max_width的区别在于：
        # max_width表示的是返回结果的最大宽度，包括了最后表示省略的点
        # str_max_width表示的是除去表示省略的符号后在输入字符串中截取部分的最大长度
        str_max_width = max_width - tail_length * get_char_width(tail)
    elif max_width and max_width == tail_length * get_char_width(tail):
        # 如果最大宽度刚好和表示省略的字符串宽度一样，那就直接返回表示省略的字符串
        return tail * tail_length
    elif max_width:
        # 如果出现提供了最大宽度但最大宽度还不如结尾表示省略的字符宽度大的时候就抛出异常
        raise AttributeError

    total_width = 0
    result = input_str

    for i in range(0, len(input_str)):
        total_width += get_char_width(input_str[i])

        if not max_width:
            continue

        # 当接近str_max_width时有几种情况：
        # 一种最离str_max_width还有一个半角字符，这种情况就继续循环
        # 另一种是截完当前字符总长度刚好为str_max_width，这种情况就停止分析下面的字符，
        # 直接在当前字符后面加上表示省略的符号后返回，这时总的长度刚好为max_width
        # 最后一种情况是截取完上一个字符后总宽度刚好和str_max_width差一个半角字符，
        # 刚好当前读取的字符的宽度是2（全角字符），那从输入字符串中截取的长度不可能和
        # str_max_width完全相同，会比str_max_width大一个半角宽度，这种情况就把表示
        # 省略的字符少显示一个，加到结尾，这样最后返回值的长度刚好也是max_width.
        if total_width < str_max_width:
            continue
        elif total_width == str_max_width:
            result = input_str[0:i + 1] + tail * tail_length
            break
        else:
            result = input_str[0:i + 1] + tail * (tail_length - 1)
            break

    return result if max_width else total_width


def format_date_str(date_str):
    try:
        return datetime.strptime(date_str, '%B %d, %Y').strftime('%Y-%m-%d')
    except Exception:
        pass
    try:
        return datetime.strptime(date_str, '%B, %Y').strftime('%Y-%m-%d')
    except Exception:
        pass

    try:
        return datetime.strptime(date_str, '%b %d, %Y').strftime('%Y-%m-%d')
    except Exception:
        pass

    try:
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
    except Exception:
        pass

    try:
        return datetime.strptime(date_str, '%Y-%m').strftime('%Y-%m-%d')
    except Exception:
        pass

    return ''

    # try:
    #     res = re.search(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', date_str)
    #     if res:
    #         return '{}-{}-{}'.format(res.group(1), res.group(2).zfill(2), res.group(3).zfill(2))
    #
    #     res = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', date_str)
    #     if res:
    #         return '{}-{}-{}'.format(res.group(3), res.group(1).zfill(2), res.group(2).zfill(2))
    #
    #     res = re.match(r'(\d{4})[/-](\d{1,2})', date_str)
    #     if res:
    #         return '{}-{}-{}'.format(res.group(1), res.group(2).zfill(2), '01')
    #     return ''
    # except:
    #     return ''


def format_time_str(time_str):
    try:
        res = re.search(r'(\d{2}):(\d{2}):(\d{2})', time_str)
        if res:
            return '{}:{}:{}'.format(res.group(1).zfill(2), res.group(2).zfill(2), res.group(3).zfill(2))
        return '00:01:00'
    except:
        return '00:01:00'


def format_date_time_str(date_time_str):
    return '{} {}'.format(format_date_str(date_time_str), format_time_str(date_time_str))


def get_res_to_bytes(res_str):
    if not res_str:
        return
    stream = QFile(res_str)
    if stream.open(QFile.ReadOnly):
        return stream.readAll()


def get_spider_metastruct():
    return {
        '标题': '',
        '电视节目标题': '',
        '集标题': '',

        '季数': '',
        '季': '',
        '集': '',

        '发布日期': '',
        '发布日期(电视节目)': '',
        '发布日期(集)': '',

        '级别': '',
        '评级': '',
        '类型': '',
        '演员': '',
        '作者': '',
        '导演': '',

        '标语': '',
        '摘要': '',

        'poster': b'',
        'backdrop': b'',
        'images': [],

        'dital_url': '',
        'tip': '',
        'id': '',
        'total': 0,
    }


def trim(im):
    try:
        bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
        diff = ImageChops.difference(im, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox:
            return im.crop(bbox)
    except Exception:
        return im


def rotate_image(in_bytes):
    try:
        out = BytesIO()
        stream = BytesIO(in_bytes)
        im = Image.open(stream)
        img2 = im.transpose(Image.ROTATE_90)
        img2.save(out, format='JPEG')
        return out.getvalue()
    except Exception:
        return in_bytes


def tim_img_bytes(in_bytes):
    try:
        out = BytesIO()
        stream = BytesIO(in_bytes)
        im = Image.open(stream)
        im = trim(im)
        if not im:
            return in_bytes
        im.save(out, format='JPEG')
        return out.getvalue()
    except:
        return in_bytes


def create_poster(in_bytes, middle=False):
    try:
        out = BytesIO()
        stream = BytesIO(in_bytes)
        im = Image.open(stream)
        im = trim(im)
        if not im:
            return None
        if im.size[0] < im.size[1]:
            im.save(out, format='JPEG')
            return out.getvalue()
        if middle:
            pos = im.size[0] // 4
        else:
            pos = im.size[0] * 420 // 800
        box = pos, 0, im.size[0], im.size[1]
        region = im.crop(box)
        region.save(out, format='JPEG')
        return out.getvalue()
    except Exception:
        return None

def merge_image(poster,bakdrop):
    try:
        out = BytesIO()


        stream = BytesIO(poster)
        im_poster = Image.open(stream)

        stream = BytesIO(bakdrop)
        im_bakdrop = Image.open(stream)


        im_bakdrop = im_bakdrop.resize(im_poster.size,Image.ANTIALIAS)

        new_im = Image.new('RGB', (im_poster.size[0] * 2, im_poster.size[1]))

        new_im.paste(im_bakdrop, (0, 0))
        new_im.paste(im_poster, (im_poster.size[0], 0))

        new_im.save(out, format='JPEG')
        return out.getvalue()
    except Exception:
        pass


if __name__ == '__main__':
    html1 ='''
    
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Fighters (2011) - Porn Movie - data18.com</title>
<link rel="alternate" type="application/atom+xml" title="ALL Movies - New Releases" href="http://www.data18.com/rss/new-movies" />
<link rel="alternate" type="application/atom+xml" title="ALL Updates - New Releases" href="http://www.data18.com/rss/new-updates" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:site" content="@data18" />
<meta name="twitter:title" content="Fighters (2011) - Porn Movie" />
<meta property="og:image" content="http://covers.data18.com/4/199947-fighters-front-dvd-bluray.jpg" />
<meta property="og:title" content="Fighters (2011) - Porn Movie" />
<meta property="og:description" content="Two beautiful, passionate girls from opposite walks of life come together in a battle of lust, raw emotion, egos and unyielding wills to fight it out in a stealthy boxing match. Gorgeous yet tough..." />
<meta property="og:site_name" content="data18" />
<meta property="og:type" content="video.movie" />
<meta property="og:url" content="http://www.data18.com/movies/99947" />
<meta name="description" content="Two beautiful, passionate girls from opposite walks of life come together in a battle of lust, raw emotion, egos and unyielding wills to fight it out in a stealthy boxing match. Gorgeous yet tough..." />
<meta name="keywords" content="fighters" />
<meta name="RATING" content="RTA-5042-1996-1400-1577-RTA" />
<link rel="stylesheet" href="http://www.data18.com/css/general.css" type="text/css" media="screen" />


<link rel="shortcut icon" href="http://www.data18.com/fav.ico" />
<script type="text/javascript">
  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-18866535-1']); 
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);      
  })();
</script>

<script src="http://www.data18.com/js/jquery-1.11.0.min.js"></script>
<script src="http://www.data18.com/js/jquery.lazyload.js"></script>
<script src="http://www.data18.com/js/feather.js"></script>
<script src="http://www.data18.com/js/tooltipster.bundle.min.js"></script>


    <script>
        $(document).ready(function() {

$('.tooltip').tooltipster({
theme: 'tooltipster-noir',
maxWidth: 290
});

        });
    </script>

<script>
        $(document).ready(function(){
        $("#listpornstarsdiv").one("mouseover", function() {
	$("#movieselectb").load("/sys/related_movies.php?s=164");
	$("#starselectb").load("/sys/related_studio.php?s=164");
    });
        });
        </script><script type="text/javascript" src="http://www.data18.com/js/jquery.fancybox.js?v=2.1.5"></script>
<script>
$(document).ready(function(){
$('#nav_movies').on('change', function() {
$("#navline").load("/sys/c_movies.php?mode=&m=99947&v="+this.value+"");
});
});
</script>
</head>
<body>
<div class="main gre1"><div id="centered" class="main2"><div class="lineup"></div><div style="background:white;padding:10px;"><div style="float: left; width: 160px; height: 66px; overflow: hidden;
 margin-top: -2px;">
<span class="red bold">Store</span>            
 &amp; <span class="red bold">Porn Database</span>

<div style="margin-top: 1px;">
<a href="http://www.data18.com"><img src="http://img.data18.com/images/logo-mini.jpg" alt="logo" /></a></div></div><div style="float: left; width: 785px; height: 60px;" class="p3"><p style="margin: 0px; width: 805px; margin-left: 0px; margin-top: -3px;">By method: <span style="background: LightGoldenRodYellow;; color: black; padding: 5px;" class="bordat"><a href="http://www.data18.com/movies/membership.html" style="text-decoration: none; color: black;">Membership</a></span>
 <span style="background: #b4d9ff; color: black; padding: 5px;" class="bordat"><a href="http://www.data18.com/movies/vod.html/pps" style="text-decoration: none; color: black;">Pay per scene</a></span>
 <span style="background: #b4d9ff; color: black; padding: 5px;" class="bordat"><a href="http://www.data18.com/movies/vod.html/own" style="text-decoration: none; color: black;">Digital Own</a></span>
 <span style="background: #b4d9ff; color: black; padding: 5px;" class="bordat"><a href="http://www.data18.com/movies/vod.html/rental" style="text-decoration: none; color: black;">Rental Movie</a></span>
 <span style="background: #b4d9ff; color: black; padding: 5px;" class="bordat"><a href="http://www.data18.com/movies/vod.html/ppm" style="text-decoration: none; color: black;">Pay per Minute</a></span>
 <span style="background: #E5E5E5; color: black; padding: 5px;" class="bordat"><a href="http://www.data18.com/movies/dvd.html" style="text-decoration: none; color: black;">DVD</a></span>
 <span style="background: #E5E5E5; color: black; padding: 5px;" class="bordat"><a href="http://www.data18.com/movies/blu-ray.html" style="text-decoration: none; color: black;">Blu-Ray</a></span></p><div style="width: 805px; margin-top: 13px; margin-bottom: -7px; margin-left: 3px;"><a href="http://www.data18.com/pornstars/" style="text-decoration: none;">
<div style="float: left; background: #DADADA; padding: 8px; margin-right: 5px;" class="bordat"
 onmouseover="this.style.background='#f0f0f0'" onmouseout="this.style.background='#DADADA'">
<span class="gen bold">Pornstars</span><br /><span class="genmed">12,670</span>
</div>
</a>

<a href="http://www.data18.com/movies/" style="text-decoration: none;">
<div style="float: left; background: #DADADA; padding: 8px; margin-right: 5px;" class="bordat"
 onmouseover="this.style.background='#f0f0f0'" onmouseout="this.style.background='#DADADA'">
<span class="gen bold">Movies</span><br /><span class="genmed">145,605</span>
</div>
</a>

<a href="http://www.data18.com/content/" style="text-decoration: none;">
<div style="float: left; background: #DADADA; padding: 8px; margin-right: 5px;" class="bordat"
 onmouseover="this.style.background='#f0f0f0'" onmouseout="this.style.background='#DADADA'">
<span class="gen bold">Scene Guide</span>  
<br /><span class="genmed">572,784 Scenes & Galleries</span>
</div>
</a>

<a href="http://www.data18.com/studios/" style="text-decoration: none;">
<div style="float: left; background: #DADADA; padding: 8px; margin-right: 5px;" class="bordat"
 onmouseover="this.style.background='#f0f0f0'" onmouseout="this.style.background='#DADADA'">
<span class="gen bold">Studios</span>
<br /><span class="genmed">1,357</span>
</div>  
</a>

<a href="http://www.data18.com/sites/" style="text-decoration: none;">
<div style="float: left; background: #DADADA; padding: 8px; margin-right: 5px;" class="bordat"
 onmouseover="this.style.background='#f0f0f0'" onmouseout="this.style.background='#DADADA'">
<span class="gen bold">Paysites</span>
<br /><span class="genmed">813</span>
</div>
</a><div style="clear: both;"></div>
</div>
</div><div style="clear: both;"></div></div><div class="lineup"></div><div style="background: #e6e6e6; width: 100%; height: 50px;">
<div style="float: left; margin-top: 3px; width: 480px; padding: 10px;">
<form action="http://www.data18.com/search/">
 &nbsp;<input id="searchform" type="text" name="k" class="form3" style="background: tranparent; font-size: 16px;"
 placeholder="Find pornstars, movies, scenes, ..." autofocus="autofocus"  />
 <input type="submit" class="gen" value="Search" />
 &nbsp;<a href="http://www.data18.com/search/">Advanced Search</a>
</form>
</div><div style="float: left; margin-top: 3px; width: 450px;padding: 10px;" class="gen11">
<form action="http://www.data18.com/connections/" method="get">
 Connections:
<input type="text" name="v1" size="22" value="" placeholder="Variable 1" class="form2"
 style="font-size: 16px;" />
 &nbsp;and&nbsp;                  
 <input type="text" name="v2" size="22" value="" placeholder="Variable 2" class="form2"
 style="font-size: 16px;" />
 <input type="submit" class="gen" value="Go" />
 <input type="hidden" name="ref" value="1" />
</form>
</div><div style="clear: both;"></div>
</div><div style="background: width: 100%;">
<p style="padding: 8px; vertical-align: middle;" class="gen12"><img src="http://img.data18.com/images/user-16.png"
 style="width: 16px; height: 16px;" alt="user" />
 &nbsp;<a href="#" data-featherlight="http://www.data18.com/sys/box-login.php" class="bold">Sign In</a>
 - <a href="#" data-featherlight="http://www.data18.com/sys/box-register.php" class="bold">Create a New Account</a>
&nbsp;&nbsp; &nbsp;<select name="forma" onchange="window.parent.parent.window.location = this.options[this.selectedIndex].value;" 
 style="margin-top: 4px;  font-family:arial; font-size:9pt; width: 100px;">
<option value="https://secure.data18.com/store/buy-60-minutes" selected="selected">Buy Minutes</option>
<option value="https://secure.data18.com/store/buy-60-minutes">Select Package:</option>
<option value="https://secure.data18.com/store/buy-15-minutes">15 minutes - $3.99</option>
<option value="https://secure.data18.com/store/buy-30-minutes">30 minutes - $6.99</option>
<option value="https://secure.data18.com/store/buy-45-minutes">45 minutes - $8.99</option>
<option value="https://secure.data18.com/store/buy-60-minutes">60 minutes - $9.99</option>
<option value="https://secure.data18.com/store/buy-120-minutes">120 minutes - $16.99</option>
<option value="https://secure.data18.com/store/buy-240-minutes">240 minutes - $28.99</option>
<option value="https://secure.data18.com/store/buy-360-minutes">360 minutes - $39.99</option>
<option value="https://secure.data18.com/store/buy-480-minutes">480 minutes - $48.99</option>
<option value="https://secure.data18.com/store/buy-960-minutes">960 minutes - $91.99</option>
<option value="https://secure.data18.com/store/buy-2200-plus-100-minutes">* Super Packages :</option>
<option value="https://secure.data18.com/store/buy-2200-plus-100-minutes">2200 minutes + 100 FREE - $199.99</option>  
<option value="https://secure.data18.com/store/buy-3900-plus-200-minutes">3900 minutes + 200 FREE - $349.99</option>
<option value="https://secure.data18.com/store/buy-5800-plus-300-minutes">5800 minutes + 300 FREE - $499.99</option>
</select>&nbsp;&nbsp;<a href="http://www.data18.com/store/ppm-how-it-works" onclick="window.open(this.href, this.target, 'width=850,height=550,top=150,left=150'); return false;" class="gen11" rel="nofollow">How it Works?</a> &nbsp;&nbsp; &nbsp;&nbsp; <a href="http://www.data18.com/store/cart-check">Cart: 0 items</a></p>
</div><div style="float: left; width: 745px;">
<div class="p8 dloc">
<a href="http://www.data18.com" class="red bold" rel="nofollow">data18</a>
 > <a href="http://www.data18.com/movies/" class="bold">Movies</a> > <a href="http://www.data18.com/studios/digital_playground/">Digital Playground</a> <i>Studio</i> 
</div>
</div>

<div style="float: left; width: 235px;">
<div class="p8 dloc" style="text-align: right;">
 
 <a href="https://twitter.com/intent/tweet?status=Fighters%20(2011)%20-%20Porn%20Movie%20http%3A%2F%2Fwww.data18.com%2Fmovies%2F199947%20via%20@data18" onclick="window.open(this.href, this.target, 'width=500,height=400, top=150,left=150'); return false;" class="bso spr-twitter block mr5" rel="nofollow"></a> 
 <a href="http://www.addtoany.com/share_save#url=http%3A%2F%2Fwww.data18.com%2Fmovies%2F199947&amp;title=Fighters%20(2011)%20-%20Porn%20Movie" onclick="window.open(this.href, this.target, 'width=700,height=600, top=150,left=150'); return false;" class="bso spr-plus block mr5" rel="nofollow"></a>
 <a href="http://www.addtoany.com/share_save#url=http%3A%2F%2Fwww.data18.com%2Fmovies%2F199947&amp;title=Fighters%20(2011)%20-%20Porn%20Movie" onclick="window.open(this.href, this.target, 'width=700,height=600, top=150,left=150'); return false;" class="block mt2 mr5" rel="nofollow"><span style="color: black;">Share this Movie</span></a>

</div>
</div>
<div style="clear: both;"></div>
<div style="background: white;" class="p8"><div style="float: left; width: 648px; height: 55px; overflow: hidden;">
<h1 style="height: 23px; overflow: hidden; font-size: 18px; margin: 3px;">Fighters</h1>
</div><div style="float: left; width: 312px; height: 57px; border-bottom: 4px solid white;
 margin-top: -8px;
 background: #e6e6e6;" class="p4">
	<div style="margin-top: 10px; margin-left: 10px;"><div id="navmovies" style="width: 310px; height: 41px; overflow: hidden;">
<div style="padding: 0px; margin-bottom: 7px; font-size: 11px;">
<b>Nav:</b>&nbsp;
 <select id="nav_movies" style="width: 160px; font-size: 12px;">               
<option value="4-164" >Digital Playground [studio]</option><option value="3-19417">Britney Beth [star]</option>
<option value="3-9559">Charles Dera [star]</option>
<option value="3-5327">Erik Everhard [star]</option>
<option value="3-739">Jesse Jane [star]</option>
<option value="3-840">Kayden Kross [star]</option>
<option value="3-12568">Manuel Ferrara [star]</option>
<option value="3-16930">Marco Rivera [star]</option>
<option value="3-16934">Ramon Nomar [star]</option>
<option value="3-14740">Riley Steele [star]</option>
<option value="3-12161">Scott Nails [star]</option>
<option value="3-8791">Stoya [star]</option>
<option value="3-12184">Tommy Gunn [star]</option>
<option value="3-17223">Toni Ribas [star]</option>
<option value="3-15221">Vicki Chase [star]</option>

</select>
<script>$(document).ready(function(){



$("#next_movie").click(function(){ window.location = 'http://www.data18.com/go/next_movie/4/164/99947'; });
$("#prev_movie").click(function(){ window.location = 'http://www.data18.com/go/prev_movie/4/164/99947'; });
$("#oldest_movie").click(function(){ window.location = 'http://www.data18.com/go/oldest_movie/4/164/99947'; });
$("#newest_movie").click(function(){ window.location = 'http://www.data18.com/go/newest_movie/4/164/99947'; });
$("#bigplayer").click(function(){ window.location = 'http://www.data18.com/sys/big.php?url=/movies/199947'; });
$("#moviescenes").click(function(){ $("#relatedvod").load("/sys/load_index.php?id=99947"); $("#framepics").removeClass('bold'); $("#moviescenes").addClass('bold');});
$("#framepics").click(function(){ $("#relatedvod").load("/sys/load_pics.php?id=99947&t="); $("#moviescenes").removeClass('bold'); $("#framepics").addClass('bold');});
$("#myvod").click(function(){ $("#relatedvod").load("/sys/load_vod.php");});
$("#myscenes").click(function(){ $("#relatedvod").load("/sys/load_scenes.php");});

});</script>
<div id="navline" style="margin-top: 7px;">
<span id="oldest_movie" class="navlink blue" title="oldest">&lt;&lt;</span>
 <span id="prev_movie" class="navlink blue">previous</span>
 - <span id="next_movie" class="navlink blue bold">next movie</span>
 <span id="newest_movie" class="navlink blue" title="newest">>></span>
 &nbsp;&nbsp;#855 <a href="http://www.data18.com/studios/digital_playground/movies.html" style="color: #BA0F20;">Show All</a></div>
</div>
</div></div>
        </div><div style="clear: both;"></div><div style="float: left; width: 650px;"><div style="background: #DADADA; padding: 10px; margin-bottom: 8px; margin-top: 0px; width: 620px;
 border-top: 3px solid #B92525;"><div class="gen12" style="background: LightGoldenRodYellow; width: 601px; height: 65px; overflow: hidden;padding: 10px;">
<div style="float: left;">
<p><span class="gen bold">Membership: <u>Digital Playground</u></span></p>

	<p class="gen11" style="margin-top: -3px;">- Over 3,328 scenes, including this movie<br />- Unlimited Streaming & Downloads<br />- <b>HD Included</b> - Instant Access
	

</div>       
<div style="float: left; padding: 6px; margin-top: 0px; margin-left: 25px;">
<div style="margin-right: 8px; background: Gold; margin-top: -3px; width: 280px; height: 45px;  padding: 7px; text-align: center; cursor: pointer;" class="bordat">
<p><a href="http://www.data18.com/go/membership_movie/864/13335" rel="nofollow" style="color: black;" class="big bold" onclick="this.target='_blank'">Join Digital Playground</a></p>
<span class="genmed">* Secure & Confidential. Easy cancel any time.</span>
</div>
</div>

<div style="clear: both;"></div>



</div><div class="gen12" style="background: lightblue; width: 605px; height: 90px; padding: 8px; margin-top: 8px; margin-bottom: -3px;"><div style="vertical align: bottom;             
 margin-right: 10px;" class="gen11">
<p style="padding: 6px;">
<span class="gen bold">Video on Demand:</span> <span class="gen11 blue bold">Full HD 1080p</span> &nbsp;* <i>Just pay for what you want</i> - Instant Access.
</p></div>
<div style="padding: 3px;"><div style="float: left; margin-right: 8px; background: #75ADF7; width: 140px; padding: 7px;
 border-radius:3px; -moz-border-radius:3px; -webkit-border-radius:3px;">
<div style="margin-bottom: 2px; margin-left: 2px;">
<a href="http://www.data18.com/movies/199947#scenes" style="color: black; text-decoration: none; color: black;">Pay <b>per Scene</b></a>
 &nbsp;<a href="http://www.data18.com/movies/199947#scenes" class="gen11 blue">Select</a></div>
&nbsp;<a href="http://www.data18.com/movies/199947#scenes" style="color: black; text-decoration: none; color: black;"><span style="font-size: 20px; color: white;">$3.99</span>&nbsp;&nbsp;
 <img src="http://img.data18.com/images/Play-16.png" width="10" height="10" alt="Streaming" />
 + <img src="http://img.data18.com/images/disk.png" width="10" height="10" alt="Download" /> 
</a></div>
<div style="float: left; margin-right: 8px; background: #75ADF7; width: 125px; padding: 7px;
 border-radius:3px; -moz-border-radius:3px; -webkit-border-radius:3px;">
<div style="margin-bottom: 2px;">
<a href="https://secure.data18.com/store/99947/streaming/7days_hd" style="text-decoration: none; color: black;" rel="nofollow"><b>Rental</b> Movie <span class="gen11"><u>7 days</u></span></a></div>
<a href="https://secure.data18.com/store/99947/streaming/7days_hd" style="text-decoration: none; color: black;" rel="nofollow">&nbsp;<span style="font-size: 20px; color: white;">$11.99</span>&nbsp;&nbsp;
 <img src="http://img.data18.com/images/Play-16.png" width="10" height="10" alt="Streaming" />
</a>
</div>
<div style="float: left; margin-right: 8px; background: #75ADF7; width: 130px; padding: 7px;
 border-radius:3px; -moz-border-radius:3px; -webkit-border-radius:3px;">
<div style="margin-bottom: 2px;"><a href="https://secure.data18.com/store/99947/download_to_own_hd" style="text-decoration: none; color: black;" rel="nofollow"><b>Buy</b> Full Movie</a></div>
<a href="https://secure.data18.com/store/99947/download_to_own_hd" style="text-decoration: none; color: black;" rel="nofollow">&nbsp;<span style="font-size: 20px; color: white;">$24.99</span>&nbsp;&nbsp;
 <img src="http://img.data18.com/images/Play-16.png" width="10" height="10" alt="Streaming" />
 + <img src="http://img.data18.com/images/disk.png" width="10" height="10" alt="Download" /> 
</a>
</div><div style="float: left; background: #75ADF7; width: 122px; padding: 7px; margin-top: 0px; overflow: hidden;
 border-radius:3px; -moz-border-radius:3px; -webkit-border-radius:3px;">
<div style="margin-bottom: 2px;">Pay <b>per Minute</b>
 &nbsp;<img src="http://img.data18.com/images/Play-16.png" width="10" height="10" alt="Streaming" />
</div>

<p style="margin-top: 3px; margin-bottom: -1px;">
 <select name="forma" onchange="window.parent.parent.window.location = this.options[this.selectedIndex].value;"
 style="font-family:arial; font-size:9pt; width: 117px;">
<option value="#" selected="selected">Select Package</option>
<option value="https://secure.data18.com/store/99947/buy-15-minutes">15 minutes - $3.99</option>
<option value="https://secure.data18.com/store/99947/buy-30-minutes">30 minutes - $6.99</option>
<option value="https://secure.data18.com/store/99947/buy-45-minutes">45 minutes - $8.99</option>
<option value="https://secure.data18.com/store/99947/buy-60-minutes">60 minutes - $9.99</option>
<option value="https://secure.data18.com/store/99947/buy-120-minutes">120 minutes - $16.99</option>
<option value="https://secure.data18.com/store/99947/buy-240-minutes">240 minutes - $28.99</option>
<option value="https://secure.data18.com/store/99947/buy-360-minutes">360 minutes - $39.99</option>
<option value="https://secure.data18.com/store/99947/buy-480-minutes">480 minutes - $48.99</option>
<option value="https://secure.data18.com/store/99947/buy-960-minutes">960 minutes - $91.99</option>
<option value="https://secure.data18.com/store/99947/buy-2200-plus-100-minutes">* Super Packages :</option>
<option value="https://secure.data18.com/store/99947/buy-2200-plus-100-minutes">2200 minutes + 100 FREE - $199.99
</option>
<option value="https://secure.data18.com/store/99947/buy-3900-plus-200-minutes">3900 minutes + 200 FREE - $349.99
</option>
<option value="https://secure.data18.com/store/99947/buy-5800-plus-300-minutes">5800 minutes + 300 FREE - $499.99
</option>
</select>
</p>

</div><div style="clear: both;"></div>
</div></div></div></div><div style="float: left; width: 318px;"><div style="background: #F3F3F3; border-top: 3px solid grey; height: 15px; padding: 12px; margin-bottom: 8px;" class="gen12">
</div><div style="background: #DADADA; width: 302px; height: 153px; overflow: hidden; margin-bottom: 6px; padding: 8px;">
<p class="gen11" style="margin-bottom: 5px;"><b>Physical Format:</b>
 Pay w/ Credit Card - Paypal<br />
Discreet & Fast Shipping. We deliver woldwide.</p>
<div style="background: #F3F3F3; min-height: 79px; margin: 3px;">
<div style="float: left; width: 60px;">
<img src="http://img.data18.com/images/border-dvd.jpg" alt="dvd" /><p class="gensmall">&nbsp;3 Disc</p></div>



<div style="float: left; width: 220px; overflow: hidden; padding: 5px;">
<p class="gen11">ID: 1582854 - UPC: 787633023704</p>

<p>
<a href="https://secure.data18.com/store/cart/dvd/199947" rel="nofollow"
 style="font-size: 15px; font-weight: bold;" class="button">BUY DVD - $29.99</a>
</p>



<p><span style="color: green;" class="bold">In Stock</span> - Ships Immediately</p>


</div>

<div style="clear: both;"></div>

</div>
<div style="background: #F3F3F3; min-height: 79px; margin: 3px; margin-top: 8px;">

<div style="float: left; width: 60px;">
<img src="http://img.data18.com/images/border-bluray.jpg" alt="bluray" /><p class="gensmall">&nbsp;3 Disc</p></div>



<div style="float: left; width: 220px; overflow: hidden; padding: 5px;">

<p>ID: 1589622 - UPC: xx1589622</p>


<p><a href="https://secure.data18.com/store/cart/bluray/199947" rel="nofollow"
 style="font-size: 14px; font-weight: bold;" class="button"
 >BUY BLURAY - $34.99</a>
</p>

 
<p><span class="gen11"><span style="color: green;" class="bold">In Stock</span> - Ships Immediately</span></p>



</div>
<div style="clear: both;"></div>

</div></div></div><div style="clear: both;"></div><div style="float: left; width: 650px;"><div style="background: #F3F3F3; width: 640px; padding: 0px; margin-bottom: 5px;"><div style="float: left; width: 230px; overflow: hidden; margin-left: 8px; margin-top: 8px; margin-bottom: 8px;"><a href="http://covers.data18.com/4/199947-fighters-front-dvd-bluray.jpg" class="grouped_elements" rel="covers" title="Fighters DVD Front Cover"><img src="http://img.data18.com/covers/digital-playground/fighters.jpg" alt="Cover" class="noborder" width="230" /></a>

<p class="genmed p4 mt4">
Click Cover to Enlarge - <a href="http://covers.data18.com/4/199947-fighters-back-dvd-bluray.jpg" class="grouped_elements" rel="covers" title="Fighters DVD Back Cover">Back Cover</a>
</p>

<p class="genmed p4;">
<span style="color: blue;">Blu-ray covers</span>:
<a href="http://covers.data18.com/4/199947-fighters-front-blu-ray.jpg" class="grouped_elements" rel="covers" title="Fighters Blu-Ray Front Cover">Front</a> -
 <a href="http://covers.data18.com/4/199947-fighters-back-blu-ray.jpg" class="grouped_elements" rel="covers" title="Fighters Blu-Ray Back Cover">Back</a>
</p></div><div style="float: left; width: 385px; margin-top: 8px;
 overflow: hidden; height: 392px;
 padding: 8px;" class="gen12"><div style="float: left; background: #DADADA; margin-top: 0px; font-size: 15px; margin-left: 3px;" class="p8 mt5">
 <a href="http://www.data18.com/movies/trailers.html/199947" style="color: black; font-size: 18px;">Play Trailer</a>
</div><div style="clear: both;"></div><div style="height: 8px;"></div><p>Production Year: 2011 | Release date: September, 2011
</p><p><b>Studio:</b> <a href="http://www.data18.com/studios/digital_playground/">Digital Playground</a> | <b>Director:</b> <a href="http://www.data18.com/search/?t=2&amp;k=nokey&amp;director=robby+d" rel="nofollow">Robby D</a></p><p><b>Movie Length</b>: 178 min. in <a href="http://www.data18.com/movies/199947#scenes">7 Scenes</a></p><p>
<b>Categories:</b> <span class="gensmall">General:</span> <a href="http://www.data18.com/movies/feature.html">Feature</a> <span class="gensmall">W/ Script</span>, <span class="gensmall">Theme:</span> <a href="http://www.data18.com/movies/fight.html">Fight</a>
</p><p class="gen12"><b>Description:</b><br />Two beautiful, passionate girls from opposite walks of life come together in a battle of lust, raw emotion, egos and unyielding wills to fight it out in a stealthy boxing match. Gorgeous yet tough Jesse Jane combats her troubled home life with her perverted, skirt chasing father, Tommy Gunn, and finds her intense desire to fight with the help of her naughty sister, Riley Steele, and compassionate coach, Scott Nails. Sexy Kayden Kross punches out her deep seated feelings with a fiery need for boxing, supported by her sexually ravenous friend Stoya and a horny young house guest. Fueled by their inner demons, Jesse and Kayden come face to face in the best performances of their careers, ready to box it out and ultimately test whose desire and passion will prevail. </p></div>
<div style="clear: both;"></div></div></div><div style="float: left; width: 318px;"><div id="related"><div style="margin-bottom: 4px; margin-left: 0px;
 margin-left: 0px; margin-top: px;">
<div style="background: #E5E5E5; margin: 0px; width: px; padding: 6px;"
 onmouseover="this.style.background='#cfcfcf'" onmouseout="this.style.background='#E6E6E6'">
<a href="http://www.data18.com/movies/199947#scenes" style="text-decoration: none; color: black;">
<div style="padding: 6px;">
<span class="gen" style="font-weight: bold;">Related Scenes [7]</span>
 <span id="gotoscene"></span><p style="margin-top: 2px;"><u>Go to Scene Index</u> for detailed information.</p>
</div>
</a></div></div><div id="style-2" style="width: px; overflow-y: scroll; height: 348px; border-bottom: 1px dashed #BA0F20; border-right: 1px dashed #BA0F20;"><a href="http://www.data18.com/content/5294897" style="text-decoration: none; color: black;" title="">
<div class="gray2" style="margin-bottom: 5px; background: #f3f3f3; width: 294; height: 70px; overflow: hidden;" onmouseover="this.style.background='#F6F4D0'" onmouseout="this.style.background='#f3f3f3'">
                <div style="float: left; width: 125px; height:65px; overflow: hidden;"><img src="http://ima3.data18.com/index/164/99947/294897/hor5.jpg" class=""  alt="scene" /></div>
                <div style="float: left; width: 162px; padding: 6px;  margin-left: 3px;
 margin-top: 2px;"><b>Scene 1</b></a>&nbsp; <a href="https://secure.data18.com/store/scene/292537" rel="nofollow"
 style="text-decoration: none; background-color: #b4d9ff; color: black; padding: 3px;" class="genmed"><b>Buy Scene</b> $3.99</a>
<a href="http://www.data18.com/content/5294897" style="text-decoration: none; color: black;" title=""><p style="margin-top: 2px;">Britney Beth</p></div>
                <div style="clear: both;"></div></div></a><a href="http://www.data18.com/content/5294898" style="text-decoration: none; color: black;" title="">
<div class="gray2" style="margin-bottom: 5px; background: #DADADA; width: 294; height: 70px; overflow: hidden;" onmouseover="this.style.background='#F6F4D0'" onmouseout="this.style.background='#DADADA'">
                <div style="float: left; width: 125px; height:65px; overflow: hidden;"><img src="http://ima3.data18.com/index/164/99947/294898/hor5.jpg" class=""  alt="scene" /></div>
                <div style="float: left; width: 162px; padding: 6px;  margin-left: 3px;
 margin-top: 2px;"><b>Scene 2</b></a>&nbsp; <a href="https://secure.data18.com/store/scene/292538" rel="nofollow"
 style="text-decoration: none; background-color: #b4d9ff; color: black; padding: 3px;" class="genmed"><b>Buy Scene</b> $3.99</a>
<a href="http://www.data18.com/content/5294898" style="text-decoration: none; color: black;" title=""><p style="margin-top: 2px;">Riley Steele</p></div>
                <div style="clear: both;"></div></div></a><a href="http://www.data18.com/content/5294899" style="text-decoration: none; color: black;" title="">
<div class="gray2" style="margin-bottom: 5px; background: #f3f3f3; width: 294; height: 70px; overflow: hidden;" onmouseover="this.style.background='#F6F4D0'" onmouseout="this.style.background='#f3f3f3'">
                <div style="float: left; width: 125px; height:65px; overflow: hidden;"><img src="http://ima3.data18.com/index/164/99947/294899/hor5.jpg" class=""  alt="scene" /></div>
                <div style="float: left; width: 162px; padding: 6px;  margin-left: 3px;
 margin-top: 2px;"><b>Scene 3</b></a>&nbsp; <a href="https://secure.data18.com/store/scene/292539" rel="nofollow"
 style="text-decoration: none; background-color: #b4d9ff; color: black; padding: 3px;" class="genmed"><b>Buy Scene</b> $3.99</a>
<a href="http://www.data18.com/content/5294899" style="text-decoration: none; color: black;" title=""><p style="margin-top: 2px;">Kayden Kross</p></div>
                <div style="clear: both;"></div></div></a><a href="http://www.data18.com/content/5294900" style="text-decoration: none; color: black;" title="">
<div class="gray2" style="margin-bottom: 5px; background: #DADADA; width: 294; height: 70px; overflow: hidden;" onmouseover="this.style.background='#F6F4D0'" onmouseout="this.style.background='#DADADA'">
                <div style="float: left; width: 125px; height:65px; overflow: hidden;"><img src="http://ima3.data18.com/index/164/99947/294900/hor5.jpg" class=""  alt="scene" /></div>
                <div style="float: left; width: 162px; padding: 6px;  margin-left: 3px;
 margin-top: 2px;"><b>Scene 4</b></a>&nbsp; <a href="https://secure.data18.com/store/scene/292540" rel="nofollow"
 style="text-decoration: none; background-color: #b4d9ff; color: black; padding: 3px;" class="genmed"><b>Buy Scene</b> $3.99</a>
<a href="http://www.data18.com/content/5294900" style="text-decoration: none; color: black;" title=""><p style="margin-top: 2px;">Stoya, Vicki Chase</p></div>
                <div style="clear: both;"></div></div></a><a href="http://www.data18.com/content/5294901" style="text-decoration: none; color: black;" title="">
<div class="gray2" style="margin-bottom: 5px; background: #f3f3f3; width: 294; height: 70px; overflow: hidden;" onmouseover="this.style.background='#F6F4D0'" onmouseout="this.style.background='#f3f3f3'">
                <div style="float: left; width: 125px; height:65px; overflow: hidden;"><img src="http://ima3.data18.com/index/164/99947/294901/hor5.jpg" class=""  alt="scene" /></div>
                <div style="float: left; width: 162px; padding: 6px;  margin-left: 3px;
 margin-top: 2px;"><b>Scene 5</b></a>&nbsp; <a href="https://secure.data18.com/store/scene/292541" rel="nofollow"
 style="text-decoration: none; background-color: #b4d9ff; color: black; padding: 3px;" class="genmed"><b>Buy Scene</b> $3.99</a>
<a href="http://www.data18.com/content/5294901" style="text-decoration: none; color: black;" title=""><p style="margin-top: 2px;">Jesse Jane</p></div>
                <div style="clear: both;"></div></div></a><a href="http://www.data18.com/content/5294902" style="text-decoration: none; color: black;" title="">
<div class="gray2" style="margin-bottom: 5px; background: #DADADA; width: 294; height: 70px; overflow: hidden;" onmouseover="this.style.background='#F6F4D0'" onmouseout="this.style.background='#DADADA'">
                <div style="float: left; width: 125px; height:65px; overflow: hidden;"><img src="http://ima3.data18.com/index/164/99947/294902/hor5.jpg" class=""  alt="scene" /></div>
                <div style="float: left; width: 162px; padding: 6px;  margin-left: 3px;
 margin-top: 2px;"><b>Scene 6</b></a>&nbsp; <a href="https://secure.data18.com/store/scene/292542" rel="nofollow"
 style="text-decoration: none; background-color: #b4d9ff; color: black; padding: 3px;" class="genmed"><b>Buy Scene</b> $3.99</a>
<a href="http://www.data18.com/content/5294902" style="text-decoration: none; color: black;" title=""><p style="margin-top: 2px;">Kayden Kross</p></div>
                <div style="clear: both;"></div></div></a><a href="http://www.data18.com/content/5294903" style="text-decoration: none; color: black;" title="">
<div class="gray2" style="background: #f3f3f3; width: 294; height: 70px; overflow: hidden;" onmouseover="this.style.background='#F6F4D0'" onmouseout="this.style.background='#f3f3f3'">
                <div style="float: left; width: 125px; height:65px; overflow: hidden;"><img src="http://ima3.data18.com/index/164/99947/294903/hor5.jpg" class=""  alt="scene" /></div>
                <div style="float: left; width: 162px; padding: 6px;  margin-left: 3px;
 margin-top: 2px;"><b>Scene 7</b></a>&nbsp; <a href="https://secure.data18.com/store/scene/292543" rel="nofollow"
 style="text-decoration: none; background-color: #b4d9ff; color: black; padding: 3px;" class="genmed"><b>Buy Scene</b> $3.99</a>
<a href="http://www.data18.com/content/5294903" style="text-decoration: none; color: black;" title=""><p style="margin-top: 2px;">Stoya</p></div>
                <div style="clear: both;"></div></div></a></div></div></div>
<div style="clear: both;"></div><div style="float: left; width: 650px;"><div style="padding: 10px; margin-top: 15px;"><p><span class="gen" style="font-weight: bold;">Cast of Fighters:</span> <span class="gen11">( In alphabetic order )</span></p>
        <div class="contenedor" style="overflow:auto; padding: 6px;">
        <div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/britney_beth/"><img src="http://img.data18.com/images/stars/60/19417.jpg" class="yborder" alt="Britney Beth" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/britney_beth/" class="gensmall">Britney Beth</a>
</p>
</div><div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/charles_dera/"><img src="http://img.data18.com/images/stars/60/9559.jpg" class="yborder" alt="Charles Dera" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/charles_dera/" class="gensmall">Charles Dera</a>
</p>
</div><div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/erik_everhard/"><img src="http://img.data18.com/images/stars/60/5327.jpg" class="yborder" alt="Erik Everhard" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/erik_everhard/" class="gensmall">Erik Everhard</a>
</p>
</div><div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/jesse_jane/"><img src="http://img.data18.com/images/stars/60/739.jpg" class="yborder" alt="Jesse Jane" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/jesse_jane/" class="gensmall">Jesse Jane</a>
</p>
</div><div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/kayden_kross/"><img src="http://img.data18.com/images/stars/60/840.jpg" class="yborder" alt="Kayden Kross" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/kayden_kross/" class="gensmall">Kayden Kross</a>
</p>
</div><div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/manuel_ferrara/"><img src="http://img.data18.com/images/stars/60/12568.jpg" class="yborder" alt="Manuel Ferrara" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/manuel_ferrara/" class="gensmall">Manuel Ferrara</a>
</p>
</div><div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/marco_rivera/"><img src="http://img.data18.com/images/stars/60/16930.jpg" class="yborder" alt="Marco Rivera" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/marco_rivera/" class="gensmall">Marco Rivera</a>
</p>
</div><div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/ramon_nomar/"><img src="http://img.data18.com/images/stars/60/16934.jpg" class="yborder" alt="Ramon Nomar" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/ramon_nomar/" class="gensmall">Ramon Nomar</a>
</p>
</div><div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/riley_steele/"><img src="http://img.data18.com/images/stars/60/14740.jpg" class="yborder" alt="Riley Steele" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/riley_steele/" class="gensmall">Riley Steele</a>
</p>
</div><div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/scott_nails/"><img src="http://img.data18.com/images/stars/60/12161.jpg" class="yborder" alt="Scott Nails" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/scott_nails/" class="gensmall">Scott Nails</a>
</p>
</div><div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/stoya/"><img src="http://img.data18.com/images/stars/60/8791.jpg" class="yborder" alt="Stoya" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/stoya/" class="gensmall">Stoya</a>
</p>
</div><div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/tommy_gunn/"><img src="http://img.data18.com/images/stars/60/12184.jpg" class="yborder" alt="Tommy Gunn" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/tommy_gunn/" class="gensmall">Tommy Gunn</a>
</p>
</div></div><div class="contenedor" style="overflow:auto; padding: 6px;"><div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/toni_ribas/"><img src="http://img.data18.com/images/stars/60/17223.jpg" class="yborder" alt="Toni Ribas" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/toni_ribas/" class="gensmall">Toni Ribas</a>
</p>
</div><div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/vicki_chase/"><img src="http://img.data18.com/images/stars/60/15221.jpg" class="yborder" alt="Vicki Chase" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/vicki_chase/" class="gensmall">Vicki Chase</a>
</p>
</div>
        </div></div></div>                
<div style="float: left; width: 318px;"><div style="margin-top: 20px;"><div style="background: #DADADA; margin: 0px; width: auto; margin-bottom: 3px; padding: 6px;">
<span class="gen" style="font-weight: bold;">Related Studio:</span>
</div>
<div style="padding: 5px; background: #F7F7F7;">
<div style="width: 308px; height: 70px; overflow: hidden;">
<div style="margin-top: -5px; margin-left: -5px;">
<a href="http://www.data18.com/studios/digital_playground/"><img src="http://img.data18.com/images/pic/digitalplayground.jpg" alt="studio" /></a>
</div>
</div></div><div id="listpornstarsdiv" style="background: #F7F7F7; padding: 6px; margin-bottom: 5px;"><p class="gen12"><a href="http://www.data18.com/studios/digital_playground/movies.html" class="bold">Movies</a> <span class="genmed">855</span>&nbsp;&nbsp;<a href="http://www.data18.com/studios/digital_playground/content.html" class="bold">Scenes</a> <span class="genmed">4,206</span>&nbsp;&nbsp;<a href="http://www.data18.com/studios/digital_playground/with.html" class="bold">Pornstars</a> <span class="genmed">1,961</span>&nbsp;</p><form action="http://www.data18.com/connections/">  
<div style="margin-left: 6px; margin-top: 5px;">
<input type="text" name="v2" maxlength="256" style="background: #DADADA; width: 190px; font-size: 16px;"
 placeholder="movies, pornstars, ..."/>
 <input type="submit" value="Search" style="font-size: 13px;" />
<input type="hidden" name="v1" value="digital playground" />
<input type="hidden" name="studioid" value="164" />
</div>
</form><div style="padding: 8px;"><b>About Digital Playground</b> 
 - Where & How:<br />
This studio offers different methods to Watch:
<p style="margin-left: 5px; margin-top: 5px;"><a href="http://www.data18.com/studios/digital_playground/membership.html">Official Membership</a> (676)</p><p style="margin-left: 5px;"><a href="http://www.data18.com/studios/digital_playground/dvd.html">DVD</a> (850) & <a href="http://www.data18.com/studios/digital_playground/dvd.html/used">Used DVDs</a> (213) - <a href="http://www.data18.com/studios/digital_playground/blu-ray.html">Blu-Ray</a> (403)</p><p style="margin-left: 5px;"><a href="http://www.data18.com/studios/digital_playground/on-demand.html">Video on Demand</a> (703)
 Own, Rental, x Minute</p><p style="margin-left: 5px;"><span class="red">New Option:</span> <a href="http://www.data18.com/studios/digital_playground/on-demand.html/scenes">Pay per Scene</a> 3630</p>
</div><div style="margin-left: 5px; margin-top: 3px; margin-bottom: 10px;" class="gen">
        <p style="font-weight: bold;" class="gen11">Performer Guide:</p>
        
<div id="starselectb">
<select style="width: 200px; padding: 3px;">
<option selected="selected">Search Pornstars...</option>
</select>
</div>
        </div><script>              
        $(document).ready(function(){
        $("#listpornstarsdiv").one("mouseover", function() {
	$("#movieselectb").load("/sys/related_movies.php?s=164");
	$("#starselectb").load("/sys/related_studio.php?s=164");
    });
        });
        </script></div></div></div>
<div style="clear: both;"></div><div style="height: 3px;"></div><div id="scenes"></div><div style="padding: 8px; margin-bottom: 3px;">
<p class="gen" style="font-weight: bold;">Scene Index:</p>
</div><div style="background: #f3f3f3; padding: 10px; margin-bottom: 3px;"
 onmouseover="this.style.background='#F6F4D0'" onmouseout="this.style.background='#f3f3f3'">
<p><span class="gen"><b>Scene 1</b></span> &nbsp;&nbsp;00:00:06 - 00:21:39</p>
<p class="gen12">&nbsp;Starring: <b><a href="http://www.data18.com/britney_beth/" class="bold">Britney Beth</a></b></p>

<div style="float: left; margin: 8px; width: 600px; overflow: hidden;">
<a href="http://www.data18.com/content/5294897" rel="nofollow"><img src="http://ima5.data18.com/index/164/99947/1/th5/03.jpg" class="yborder" alt="image1 scene Array" /></a>&nbsp;&nbsp;<a href="http://www.data18.com/content/5294897" rel="nofollow"><img src="http://ima5.data18.com/index/164/99947/1/th5/06.jpg" class="yborder" alt="image1 scene Array" /></a>&nbsp;&nbsp;<a href="http://www.data18.com/content/5294897" rel="nofollow"><img src="http://ima5.data18.com/index/164/99947/1/th5/09.jpg" class="yborder" alt="image1 scene Array" /></a>
</div><div style="float: left; width: 300px; height: 125px; overflow: hidden;"><div style="margin-top: 8px; background: lightblue; padding: 12px;">
<a href="https://secure.data18.com/store/scene/292537" rel="nofollow" class="big bold"
 style="color: black;">Buy this scene - $3.99</a>
<p>Unlimited Download & Streaming<br />Available for life on your VOD Library</p>
</div>
</div><div style="clear: both;"></div>
</div><div style="background: #DADADA; padding: 10px; margin-bottom: 3px;"
 onmouseover="this.style.background='#F6F4D0'" onmouseout="this.style.background='#DADADA'">
<p><span class="gen"><b>Scene 2</b></span> &nbsp;&nbsp;00:21:40 - 00:39:17</p>
<p class="gen12">&nbsp;Starring: <b><a href="http://www.data18.com/riley_steele/" class="bold">Riley Steele</a></b></p>

<div style="float: left; margin: 8px; width: 600px; overflow: hidden;">
<a href="http://www.data18.com/content/5294898" rel="nofollow"><img src="http://ima5.data18.com/index/164/99947/2/th5/03.jpg" class="yborder" alt="image1 scene Array" /></a>&nbsp;&nbsp;<a href="http://www.data18.com/content/5294898" rel="nofollow"><img src="http://ima5.data18.com/index/164/99947/2/th5/06.jpg" class="yborder" alt="image1 scene Array" /></a>&nbsp;&nbsp;<a href="http://www.data18.com/content/5294898" rel="nofollow"><img src="http://ima5.data18.com/index/164/99947/2/th5/09.jpg" class="yborder" alt="image1 scene Array" /></a>
</div><div style="float: left; width: 300px; height: 125px; overflow: hidden;"><div style="margin-top: 8px; background: lightblue; padding: 12px;">
<a href="https://secure.data18.com/store/scene/292538" rel="nofollow" class="big bold"
 style="color: black;">Buy this scene - $3.99</a>
<p>Unlimited Download & Streaming<br />Available for life on your VOD Library</p>
</div>
</div><div style="clear: both;"></div>
</div><div style="background: #f3f3f3; padding: 10px; margin-bottom: 3px;"
 onmouseover="this.style.background='#F6F4D0'" onmouseout="this.style.background='#f3f3f3'">
<p><span class="gen"><b>Scene 3</b></span> &nbsp;&nbsp;00:39:17 - 01:01:08</p>
<p class="gen12">&nbsp;Starring: <b><a href="http://www.data18.com/kayden_kross/" class="bold">Kayden Kross</a></b></p>

<div style="float: left; margin: 8px; width: 600px; overflow: hidden;">
<a href="http://www.data18.com/content/5294899" rel="nofollow"><img src="http://ima5.data18.com/index/164/99947/3/th5/03.jpg" class="yborder" alt="image1 scene Array" /></a>&nbsp;&nbsp;<a href="http://www.data18.com/content/5294899" rel="nofollow"><img src="http://ima5.data18.com/index/164/99947/3/th5/06.jpg" class="yborder" alt="image1 scene Array" /></a>&nbsp;&nbsp;<a href="http://www.data18.com/content/5294899" rel="nofollow"><img src="http://ima5.data18.com/index/164/99947/3/th5/09.jpg" class="yborder" alt="image1 scene Array" /></a>
</div><div style="float: left; width: 300px; height: 125px; overflow: hidden;"><div style="margin-top: 8px; background: lightblue; padding: 12px;">
<a href="https://secure.data18.com/store/scene/292539" rel="nofollow" class="big bold"
 style="color: black;">Buy this scene - $3.99</a>
<p>Unlimited Download & Streaming<br />Available for life on your VOD Library</p>
</div>
</div><div style="clear: both;"></div>
</div><div style="background: #DADADA; padding: 10px; margin-bottom: 3px;"
 onmouseover="this.style.background='#F6F4D0'" onmouseout="this.style.background='#DADADA'">
<p><span class="gen"><b>Scene 4</b></span> &nbsp;&nbsp;01:01:08 - 01:36:09</p>
<p class="gen12">&nbsp;Starring: <b><a href="http://www.data18.com/stoya/" class="bold">Stoya</a>, <a href="http://www.data18.com/vicki_chase/" class="bold">Vicki Chase</a></b></p>

<div style="float: left; margin: 8px; width: 600px; overflow: hidden;">
<a href="http://www.data18.com/content/5294900" rel="nofollow"><img src="http://ima5.data18.com/index/164/99947/4/th5/03.jpg" class="yborder" alt="image1 scene Array" /></a>&nbsp;&nbsp;<a href="http://www.data18.com/content/5294900" rel="nofollow"><img src="http://ima5.data18.com/index/164/99947/4/th5/06.jpg" class="yborder" alt="image1 scene Array" /></a>&nbsp;&nbsp;<a href="http://www.data18.com/content/5294900" rel="nofollow"><img src="http://ima5.data18.com/index/164/99947/4/th5/09.jpg" class="yborder" alt="image1 scene Array" /></a>
</div><div style="float: left; width: 300px; height: 125px; overflow: hidden;"><div style="margin-top: 8px; background: lightblue; padding: 12px;">
<a href="https://secure.data18.com/store/scene/292540" rel="nofollow" class="big bold"
 style="color: black;">Buy this scene - $3.99</a>
<p>Unlimited Download & Streaming<br />Available for life on your VOD Library</p>
</div>
</div><div style="clear: both;"></div>
</div><div style="background: #f3f3f3; padding: 10px; margin-bottom: 3px;"
 onmouseover="this.style.background='#F6F4D0'" onmouseout="this.style.background='#f3f3f3'">
<p><span class="gen"><b>Scene 5</b></span> &nbsp;&nbsp;01:36:09 - 02:12:10</p>
<p class="gen12">&nbsp;Starring: <b><a href="http://www.data18.com/jesse_jane/" class="bold">Jesse Jane</a></b></p>

<div style="float: left; margin: 8px; width: 600px; overflow: hidden;">
<a href="http://www.data18.com/content/5294901" rel="nofollow"><img src="http://ima5.data18.com/index/164/99947/5/th5/03.jpg" class="yborder" alt="image1 scene Array" /></a>&nbsp;&nbsp;<a href="http://www.data18.com/content/5294901" rel="nofollow"><img src="http://ima5.data18.com/index/164/99947/5/th5/06.jpg" class="yborder" alt="image1 scene Array" /></a>&nbsp;&nbsp;<a href="http://www.data18.com/content/5294901" rel="nofollow"><img src="http://ima5.data18.com/index/164/99947/5/th5/09.jpg" class="yborder" alt="image1 scene Array" /></a>
</div><div style="float: left; width: 300px; height: 125px; overflow: hidden;"><div style="margin-top: 8px; background: lightblue; padding: 12px;">
<a href="https://secure.data18.com/store/scene/292541" rel="nofollow" class="big bold"
 style="color: black;">Buy this scene - $3.99</a>
<p>Unlimited Download & Streaming<br />Available for life on your VOD Library</p>
</div>
</div><div style="clear: both;"></div>
</div><div style="background: #DADADA; padding: 10px; margin-bottom: 3px;"
 onmouseover="this.style.background='#F6F4D0'" onmouseout="this.style.background='#DADADA'">
<p><span class="gen"><b>Scene 6</b></span> &nbsp;&nbsp;02:12:10 - 02:29:28</p>
<p class="gen12">&nbsp;Starring: <b><a href="http://www.data18.com/kayden_kross/" class="bold">Kayden Kross</a></b></p>

<div style="float: left; margin: 8px; width: 600px; overflow: hidden;">
<a href="http://www.data18.com/content/5294902" rel="nofollow"><img src="http://ima5.data18.com/index/164/99947/6/th5/03.jpg" class="yborder" alt="image1 scene Array" /></a>&nbsp;&nbsp;<a href="http://www.data18.com/content/5294902" rel="nofollow"><img src="http://ima5.data18.com/index/164/99947/6/th5/06.jpg" class="yborder" alt="image1 scene Array" /></a>&nbsp;&nbsp;<a href="http://www.data18.com/content/5294902" rel="nofollow"><img src="http://ima5.data18.com/index/164/99947/6/th5/09.jpg" class="yborder" alt="image1 scene Array" /></a>
</div><div style="float: left; width: 300px; height: 125px; overflow: hidden;"><div style="margin-top: 8px; background: lightblue; padding: 12px;">
<a href="https://secure.data18.com/store/scene/292542" rel="nofollow" class="big bold"
 style="color: black;">Buy this scene - $3.99</a>
<p>Unlimited Download & Streaming<br />Available for life on your VOD Library</p>
</div>
</div><div style="clear: both;"></div>
</div><div style="background: #f3f3f3; padding: 10px; margin-bottom: 3px;"
 onmouseover="this.style.background='#F6F4D0'" onmouseout="this.style.background='#f3f3f3'">
<p><span class="gen"><b>Scene 7</b></span> &nbsp;&nbsp;02:29:28 - 02:57:52</p>
<p class="gen12">&nbsp;Starring: <b><a href="http://www.data18.com/stoya/" class="bold">Stoya</a></b></p>

<div style="float: left; margin: 8px; width: 600px; overflow: hidden;">
<a href="http://www.data18.com/content/5294903" rel="nofollow"><img src="http://ima5.data18.com/index/164/99947/7/th5/03.jpg" class="yborder" alt="image1 scene Array" /></a>&nbsp;&nbsp;<a href="http://www.data18.com/content/5294903" rel="nofollow"><img src="http://ima5.data18.com/index/164/99947/7/th5/06.jpg" class="yborder" alt="image1 scene Array" /></a>&nbsp;&nbsp;<a href="http://www.data18.com/content/5294903" rel="nofollow"><img src="http://ima5.data18.com/index/164/99947/7/th5/09.jpg" class="yborder" alt="image1 scene Array" /></a>
</div><div style="float: left; width: 300px; height: 125px; overflow: hidden;"><div style="margin-top: 8px; background: lightblue; padding: 12px;">
<a href="https://secure.data18.com/store/scene/292543" rel="nofollow" class="big bold"
 style="color: black;">Buy this scene - $3.99</a>
<p>Unlimited Download & Streaming<br />Available for life on your VOD Library</p>
</div>
</div><div style="clear: both;"></div>
</div><div style="height: 50px;"></div><div style="width: 900px; padding: 8px; margin-bottom: 10px;">
<p><span class="big bold">18 U.S.C.Section 2257 Compliance Statement:</span></p>
<p class="gen12">All models were at least 18 years old when they were photographed &amp; shooted.</p><p class="gen12">
Information from our official store: <a href="http://www.data18.com/store/help/cs_2257" onclick="window.open(this.href, this.target, 'width=995,height=400,top=150,left=150'); return false;"  rel="nofollow">Click Here for 18 U.S.C. 2257 information </a></p><p class="gen12">* Membership option: Digital Playground and related sites are not operated by data18</p>
<p style="margin-top: -3px;">For more information about
 <span style="text-decoration: underline;">18 U.S.C.Section 2257 Compliance Statement</span>
please visit:
 <a href="http://www.data18.com/go/864" rel="nofollow" class="bold" onclick="this.target='_blank'">
Digital Playground</a>
</p></div></div><div style="clear: both;"></div><div style="height: 275px; background: #f3f3f3; margin-top: 3px; padding: 10px; text-align: center;"><div style="width: 310px; height: 72px; overflow: hidden; margin-bottom: 10px;">
<div style="margin-top: -4px; margin-left: -4px;">
<a href="http://www.data18.com/studios/digital_playground/"><img src="http://img.data18.com/images/pic/digitalplayground.jpg" alt="studio" /></a>
</div>
</div><div style="float: left; padding: 8px;">
<a href="http://www.data18.com/movies/1157086"><img src="http://img.data18.com/covers/nav/7/1157086-teen-swap.jpg" style="width: 120px;" /></a>
</div> <div style="float: left; padding: 8px;">
<a href="http://www.data18.com/movies/1156968"><img src="http://img.data18.com/covers/nav/7/1156968-filthy-fucks-2.jpg" style="width: 120px;" /></a>
</div> <div style="float: left; padding: 8px;">
<a href="http://www.data18.com/movies/1156823"><img src="http://img.data18.com/covers/nav/7/1156823-blown-away.jpg" style="width: 120px;" /></a>
</div> <div style="float: left; padding: 8px;">
<a href="http://www.data18.com/movies/1156416"><img src="http://img.data18.com/covers/nav/7/1156416-ski-bums.jpg" style="width: 120px;" /></a>
</div> <div style="float: left; padding: 8px;">
<a href="http://www.data18.com/movies/1156415"><img src="http://img.data18.com/covers/nav/7/1156415-rina-ellis-saves-world-xxx-90s-parody.jpg" style="width: 120px;" /></a>
</div> <div style="float: left; padding: 8px;">
<a href="http://www.data18.com/movies/1156266"><img src="http://img.data18.com/covers/nav/7/1156266-my-pie-tastes-better.jpg" style="width: 120px;" /></a>
</div> <div style="float: left; padding: 8px;">
<a href="http://www.data18.com/movies/1155984"><img src="http://img.data18.com/covers/nav/7/1155984-pornstar-confessions.jpg" style="width: 120px;" /></a>
</div> <div style="clear: both;"></div></div><div style="width: 984; height: 296px; 
 background: #F7F7F7; margin-top: 3px; overflow: hidden;">
<a href="http://www.data18.com/go/banner/864" rel="nofollow" onclick="this.target='_blank'">         <img src="http://img.data18.com/blocks/7640.jpg" alt="Digital Playground" class="noborder" /></a>

</div><div class="lfoo"><div class="block auto">
<a href="http://www.data18.com/movies/199947#" rel="nofollow" onclick="javascript: window.scrollTo(0,0);" class="gen12 bold">Back to Top</a>
</div>
</div>
<div class="clear"></div>
<div class="dfoo1">
<p class="gen bold">About data18.com</p>
<p><a href="http://www.data18.com/sys/report.php" rel="nofollow" onclick="this.target='_blank'" class="bold">Contact Us</a> - <a href="http://www.data18.com/2257.html" rel="nofollow" onclick="this.target='_blank'" class="bold">18 U.S.C. 2257</a></p>
<p>Do you like data18? <a href="http://www.data18.com/share.html" rel="nofollow" class="bold" onclick="this.target='_blank'">Share us!</a></p>
<p>Follow us: <a href="http://www.data18.com/rss.html" class="red" rel="nofollow">RSS Feeds</a> - <a href="http://www.twitter.com/data18" class="blue" rel="nofollow" onclick="this.target='_blank'">Twitter</a> @data18</p>
<p>We support the use of filtering software which prevents minors from accessing inappropriate material: <a href="http://cyberpatrol.com" rel="nofollow" onclick="this.target='_blank'">CyberPatrol</a> | <a href="http://www.pandasecurity.com/about/social-responsibility/children-internet/" rel="nofollow" onclick="this.target='_blank'">Panda</a> | <a href="http://www.netnanny.com" rel="nofollow" onclick="this.target='_blank'">Net Nanny</a></p>
</div>
<div class="dfoo2">
<p><a href="http://www.data18.com/sitemap.html" class="gen bold">Sitemap</a></p>
<p>- <a href="http://www.data18.com/pornstars/">Pornstars</a></p>
<p>- <a href="http://www.data18.com/movies/">Movies</a> </p>
<p>- <a href="http://www.data18.com/studios/">Studios</a></p>
<p>- <a href="http://www.data18.com/content/">Content</a> </p>
<p>- <a href="http://www.data18.com/sites/">Sites &amp; Networks</a></p>
<p>- <a href="http://www.data18.com/awards/">Porn Awards</a></p>
</div>
<div class="dfoo3">
<p class="gen bold">About our Store:</p>
<p>Buy <a href="http://www.data18.com/movies/dvd.html" class="bold">DVDs</a>, <a href="http://www.data18.com/movies/blu-ray.html" class="bold">Blu-Ray</a>, <a href="http://www.data18.com/movies/vod.html" class="bold">Video on Demand</a> and <a href="http://www.data18.com/sex-toys/" class="bold">Sex Toys</a>.</p>
<p>The Store is provided by <a href="http://www.adultempirecash.com" rel="nofollow" onclick="this.target='_blank'">Empire Stores</a>:<br /><a href="http://www.data18.com/store/help/cs_2257" onclick="window.open(this.href, this.target, 'width=980,height=400,top=150,left=150'); return false;"  rel="nofollow">18 U.S.C. 2257</a> - <a href="http://www.data18.com/store/help/terms_of_use" onclick="window.open(this.href, this.target, 'width=980,height=600,top=150,left=150'); return false;"  rel="nofollow">Terms of Use</a> - <a href="http://www.data18.com/store/help/privacy_policy" onclick="window.open(this.href, this.target, 'width=980,height=600,top=150,left=150'); return false;"  rel="nofollow">Privacy Policy</a></p>
<p> Visit our store in "Full Mode", <a href="http://store.data18.com" rel="nofollow" onclick="this.target='_blank'">Click Here</a></p>
<p><span class="bold">Customer Service:</span> <a href="http://www.data18.com/store/help" rel="nofollow">Help Center</a> <a href="http://store.data18.com/account/inquiry" rel="nofollow" onclick="this.target='_blank'">Ask a Question</a> <a href="http://www.data18.com/store/help" rel="nofollow">Chat live</a></p>
<p><a href="http://www.data18.com/store/help/discreet_service" rel="nofollow">Discreet Service</a> - <a href="http://www.data18.com/store/help/shipping" rel="nofollow">Shipping Methods and Rates</a> - <a href="http://www.data18.com/store/help/return_policy" rel="nofollow">Return Policy</a>
</p>           
</div><div class="dsecure genmed">
<div class="bso spr-secure"></div>
<p>Transaction process is safe and customers' information is secure.</p>
<p>data18 encrypts confidential information with the Secure Sockets Layer (SSL)</p>
</div>
<div class="clear"></div>
</div>
</div>
<script type="text/javascript">
$(document).ready(function() {
$("a.grouped_elements").fancybox();
$("#searchform").focus();
});      


</script><div id="finalbody"></div>






</body>
</html>



    '''
    html2 = '''
        <!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>The Private Life of Jodie Moore (2003) - Porn Movie Compilation - data18.com</title>
<link rel="alternate" type="application/atom+xml" title="ALL Movies - New Releases" href="http://www.data18.com/rss/new-movies" />
<link rel="alternate" type="application/atom+xml" title="ALL Updates - New Releases" href="http://www.data18.com/rss/new-updates" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:site" content="@data18" />
<meta name="twitter:title" content="The Private Life of Jodie Moore (2003) - Porn Movie Compilation" />
<meta property="og:image" content="http://covers.data18.com/3/154497-the-private-life-of-jodie-moore-front-dvd.jpg" />
<meta property="og:title" content="The Private Life of Jodie Moore (2003) - Porn Movie Compilation" />
<meta property="og:description" content="HARDCORE XXX SEX ACTION! 2-DISC COLLECTOR'S EDITION. Discover all of Jodie Moore's finest scenes for Private and find out her sexiest secrets!" />
<meta property="og:site_name" content="data18" />
<meta property="og:type" content="video.movie" />
<meta property="og:url" content="http://www.data18.com/movies/54497" />
<meta name="description" content="HARDCORE XXX SEX ACTION! 2-DISC COLLECTOR'S EDITION. Discover all of Jodie Moore's finest scenes for Private and find out her sexiest secrets!" />
<meta name="keywords" content="the private life of jodie moore" />
<meta name="RATING" content="RTA-5042-1996-1400-1577-RTA" />
<link rel="stylesheet" href="http://www.data18.com/css/general.css" type="text/css" media="screen" />


<link rel="shortcut icon" href="http://www.data18.com/fav.ico" />
<script type="text/javascript">
  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-18866535-1']); 
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);      
  })();
</script>

<script src="http://www.data18.com/js/jquery-1.11.0.min.js"></script>
<script src="http://www.data18.com/js/jquery.lazyload.js"></script>
<script src="http://www.data18.com/js/feather.js"></script>
<script src="http://www.data18.com/js/tooltipster.bundle.min.js"></script>


    <script>
        $(document).ready(function() {

$('.tooltip').tooltipster({
theme: 'tooltipster-noir',
maxWidth: 290
});

        });
    </script>

<script>
        $(document).ready(function(){
        $("#listpornstarsdiv").one("mouseover", function() {
	$("#movieselectb").load("/sys/related_movies.php?s=457");
	$("#starselectb").load("/sys/related_studio.php?s=457");
    });
        });
        </script><script type="text/javascript" src="http://www.data18.com/js/jquery.fancybox.js?v=2.1.5"></script>
<script>
$(document).ready(function(){
$('#nav_movies').on('change', function() {
$("#navline").load("/sys/c_movies.php?mode=&m=54497&v="+this.value+"");
});
});
</script>
</head>
<body>
<script type="text/javascript">
function hide(obj) {
var el = document.getElementById(obj);
el.style.display = 'none';
}
</script>
<div id="cookiealert" class="gen">
<b>Warning:</b>
<span class="red bold">
 You must be 18 or older to visit this website</span>. If not, <a href="http://www.google.com" rel="nofollow" class="bold">
please exit</a>.<br />
data18.com uses cookies to provide and improve your experience. By continuing to use this site, you agree to accept these cookies.
 <span class="point under" onclick="hide('cookiealert')"><b>Close this tab</b></span>
</div><div class="main gre1"><div id="centered" class="main2"><div class="lineup"></div><div style="background:white;padding:10px;"><div style="float: left; width: 160px; height: 66px; overflow: hidden;
 margin-top: -2px;">
<span class="red bold">Store</span>            
 &amp; <span class="red bold">Porn Database</span>

<div style="margin-top: 1px;">
<a href="http://www.data18.com"><img src="http://img.data18.com/images/logo-mini.jpg" alt="logo" /></a></div></div><div style="float: left; width: 785px; height: 60px;" class="p3"><p style="margin: 0px; width: 805px; margin-left: 0px; margin-top: -3px;">By method: <span style="background: LightGoldenRodYellow;; color: black; padding: 5px;" class="bordat"><a href="http://www.data18.com/movies/membership.html" style="text-decoration: none; color: black;">Membership</a></span>
 <span style="background: #b4d9ff; color: black; padding: 5px;" class="bordat"><a href="http://www.data18.com/movies/vod.html/pps" style="text-decoration: none; color: black;">Pay per scene</a></span>
 <span style="background: #b4d9ff; color: black; padding: 5px;" class="bordat"><a href="http://www.data18.com/movies/vod.html/own" style="text-decoration: none; color: black;">Digital Own</a></span>
 <span style="background: #b4d9ff; color: black; padding: 5px;" class="bordat"><a href="http://www.data18.com/movies/vod.html/rental" style="text-decoration: none; color: black;">Rental Movie</a></span>
 <span style="background: #b4d9ff; color: black; padding: 5px;" class="bordat"><a href="http://www.data18.com/movies/vod.html/ppm" style="text-decoration: none; color: black;">Pay per Minute</a></span>
 <span style="background: #E5E5E5; color: black; padding: 5px;" class="bordat"><a href="http://www.data18.com/movies/dvd.html" style="text-decoration: none; color: black;">DVD</a></span>
 <span style="background: #E5E5E5; color: black; padding: 5px;" class="bordat"><a href="http://www.data18.com/movies/blu-ray.html" style="text-decoration: none; color: black;">Blu-Ray</a></span></p><div style="width: 805px; margin-top: 13px; margin-bottom: -7px; margin-left: 3px;"><a href="http://www.data18.com/pornstars/" style="text-decoration: none;">
<div style="float: left; background: #DADADA; padding: 8px; margin-right: 5px;" class="bordat"
 onmouseover="this.style.background='#f0f0f0'" onmouseout="this.style.background='#DADADA'">
<span class="gen bold">Pornstars</span><br /><span class="genmed">12,670</span>
</div>
</a>

<a href="http://www.data18.com/movies/" style="text-decoration: none;">
<div style="float: left; background: #DADADA; padding: 8px; margin-right: 5px;" class="bordat"
 onmouseover="this.style.background='#f0f0f0'" onmouseout="this.style.background='#DADADA'">
<span class="gen bold">Movies</span><br /><span class="genmed">145,605</span>
</div>
</a>

<a href="http://www.data18.com/content/" style="text-decoration: none;">
<div style="float: left; background: #DADADA; padding: 8px; margin-right: 5px;" class="bordat"
 onmouseover="this.style.background='#f0f0f0'" onmouseout="this.style.background='#DADADA'">
<span class="gen bold">Scene Guide</span>  
<br /><span class="genmed">572,784 Scenes & Galleries</span>
</div>
</a>

<a href="http://www.data18.com/studios/" style="text-decoration: none;">
<div style="float: left; background: #DADADA; padding: 8px; margin-right: 5px;" class="bordat"
 onmouseover="this.style.background='#f0f0f0'" onmouseout="this.style.background='#DADADA'">
<span class="gen bold">Studios</span>
<br /><span class="genmed">1,357</span>
</div>  
</a>

<a href="http://www.data18.com/sites/" style="text-decoration: none;">
<div style="float: left; background: #DADADA; padding: 8px; margin-right: 5px;" class="bordat"
 onmouseover="this.style.background='#f0f0f0'" onmouseout="this.style.background='#DADADA'">
<span class="gen bold">Paysites</span>
<br /><span class="genmed">813</span>
</div>
</a><div style="clear: both;"></div>
</div>
</div><div style="clear: both;"></div></div><div class="lineup"></div><div style="background: #e6e6e6; width: 100%; height: 50px;">
<div style="float: left; margin-top: 3px; width: 480px; padding: 10px;">
<form action="http://www.data18.com/search/">
 &nbsp;<input id="searchform" type="text" name="k" class="form3" style="background: tranparent; font-size: 16px;"
 placeholder="Find pornstars, movies, scenes, ..." autofocus="autofocus"  />
 <input type="submit" class="gen" value="Search" />
 &nbsp;<a href="http://www.data18.com/search/">Advanced Search</a>
</form>
</div><div style="float: left; margin-top: 3px; width: 450px;padding: 10px;" class="gen11">
<form action="http://www.data18.com/connections/" method="get">
 Connections:
<input type="text" name="v1" size="22" value="" placeholder="Variable 1" class="form2"
 style="font-size: 16px;" />
 &nbsp;and&nbsp;                  
 <input type="text" name="v2" size="22" value="" placeholder="Variable 2" class="form2"
 style="font-size: 16px;" />
 <input type="submit" class="gen" value="Go" />
 <input type="hidden" name="ref" value="1" />
</form>
</div><div style="clear: both;"></div>
</div><div style="background: width: 100%;">
<p style="padding: 8px; vertical-align: middle;" class="gen12"><img src="http://img.data18.com/images/user-16.png"
 style="width: 16px; height: 16px;" alt="user" />
Traceback (most recent call last):
 &nbsp;<a href="#" data-featherlight="http://www.data18.com/sys/box-login.php" class="bold">Sign In</a>
  File "/Users/syaofox/PycharmProjects/Synology_VideoStation_Master/utils.py", line 1551, in <module>
    soup = BeautifulSoup(html, "lxml")
 - <a href="#" data-featherlight="http://www.data18.com/sys/box-register.php" class="bold">Create a New Account</a>
&nbsp;&nbsp; &nbsp;<select name="forma" onchange="window.parent.parent.window.location = this.options[this.selectedIndex].value;" 
  File "/Users/syaofox/pycode/env1/lib/python3.6/site-packages/bs4/__init__.py", line 192, in __init__
 style="margin-top: 4px;  font-family:arial; font-size:9pt; width: 100px;">
    elif len(markup) <= 256 and (
<option value="https://secure.data18.com/store/buy-60-minutes" selected="selected">Buy Minutes</option>
TypeError: object of type 'Response' has no len()
<option value="https://secure.data18.com/store/buy-60-minutes">Select Package:</option>
<option value="https://secure.data18.com/store/buy-15-minutes">15 minutes - $3.99</option>
<option value="https://secure.data18.com/store/buy-30-minutes">30 minutes - $6.99</option>
<option value="https://secure.data18.com/store/buy-45-minutes">45 minutes - $8.99</option>
<option value="https://secure.data18.com/store/buy-60-minutes">60 minutes - $9.99</option>
<option value="https://secure.data18.com/store/buy-120-minutes">120 minutes - $16.99</option>
<option value="https://secure.data18.com/store/buy-240-minutes">240 minutes - $28.99</option>
<option value="https://secure.data18.com/store/buy-360-minutes">360 minutes - $39.99</option>
<option value="https://secure.data18.com/store/buy-480-minutes">480 minutes - $48.99</option>
<option value="https://secure.data18.com/store/buy-960-minutes">960 minutes - $91.99</option>
<option value="https://secure.data18.com/store/buy-2200-plus-100-minutes">* Super Packages :</option>
<option value="https://secure.data18.com/store/buy-2200-plus-100-minutes">2200 minutes + 100 FREE - $199.99</option>  
<option value="https://secure.data18.com/store/buy-3900-plus-200-minutes">3900 minutes + 200 FREE - $349.99</option>
<option value="https://secure.data18.com/store/buy-5800-plus-300-minutes">5800 minutes + 300 FREE - $499.99</option>
</select>&nbsp;&nbsp;<a href="http://www.data18.com/store/ppm-how-it-works" onclick="window.open(this.href, this.target, 'width=850,height=550,top=150,left=150'); return false;" class="gen11" rel="nofollow">How it Works?</a> &nbsp;&nbsp; &nbsp;&nbsp; <a href="http://www.data18.com/store/cart-check">Cart: 0 items</a></p>
</div><div style="float: left; width: 745px;">
<div class="p8 dloc">
<a href="http://www.data18.com" class="red bold" rel="nofollow">data18</a>
 > <a href="http://www.data18.com/movies/" class="bold">Movies</a> > <a href="http://www.data18.com/studios/private/">Private</a> <i>Studio</i> 
</div>
</div>

<div style="float: left; width: 235px;">
<div class="p8 dloc" style="text-align: right;">
 
 <a href="https://twitter.com/intent/tweet?status=The%20Private%20Life%20of%20Jodie%20Moore%20(2003)%20-%20Porn%20Movie%20Compilation%20http%3A%2F%2Fwww.data18.com%2Fmovies%2F154497%20via%20@data18" onclick="window.open(this.href, this.target, 'width=500,height=400, top=150,left=150'); return false;" class="bso spr-twitter block mr5" rel="nofollow"></a> 
 <a href="http://www.addtoany.com/share_save#url=http%3A%2F%2Fwww.data18.com%2Fmovies%2F154497&amp;title=The%20Private%20Life%20of%20Jodie%20Moore%20(2003)%20-%20Porn%20Movie%20Compilation" onclick="window.open(this.href, this.target, 'width=700,height=600, top=150,left=150'); return false;" class="bso spr-plus block mr5" rel="nofollow"></a>
 <a href="http://www.addtoany.com/share_save#url=http%3A%2F%2Fwww.data18.com%2Fmovies%2F154497&amp;title=The%20Private%20Life%20of%20Jodie%20Moore%20(2003)%20-%20Porn%20Movie%20Compilation" onclick="window.open(this.href, this.target, 'width=700,height=600, top=150,left=150'); return false;" class="block mt2 mr5" rel="nofollow"><span style="color: black;">Share this Movie</span></a>

</div>
</div>
<div style="clear: both;"></div>
<div style="background: white;" class="p8"><div style="float: left; width: 648px; height: 55px; overflow: hidden;">
<h1 style="height: 23px; overflow: hidden; font-size: 18px; margin: 3px;">The Private Life of Jodie Moore</h1>
</div><div style="float: left; width: 312px; height: 57px; border-bottom: 4px solid white;
 margin-top: -8px;
 background: #e6e6e6;" class="p4">
	<div style="margin-top: 10px; margin-left: 10px;"><div id="navmovies" style="width: 310px; height: 41px; overflow: hidden;">
<div style="padding: 0px; margin-bottom: 7px; font-size: 11px;">
<b>Nav:</b>&nbsp;
 <select id="nav_movies" style="width: 160px; font-size: 12px;">               
<option value="4-457" >Private [studio]</option><option value="3-4579">Alberto Rey [star]</option>
<option value="3-237">Bobbi Eden [star]</option>
<option value="3-10121">Elza Brown [star]</option>
<option value="3-770">Jodie Moore [star]</option>
<option value="3-1070">Mandy Bright [star]</option>
<option value="3-17502">Philippe Dean [star]</option>
<option value="3-24745">Sebastian Barrio [star]</option>
<option value="3-7152">Tyce Bune [star]</option>

</select>
<script>$(document).ready(function(){



$("#next_movie").click(function(){ window.location = 'http://www.data18.com/go/next_movie/4/457/54497'; });
$("#prev_movie").click(function(){ window.location = 'http://www.data18.com/go/prev_movie/4/457/54497'; });
$("#oldest_movie").click(function(){ window.location = 'http://www.data18.com/go/oldest_movie/4/457/54497'; });
$("#newest_movie").click(function(){ window.location = 'http://www.data18.com/go/newest_movie/4/457/54497'; });
$("#bigplayer").click(function(){ window.location = 'http://www.data18.com/sys/big.php?url=/movies/154497'; });
$("#moviescenes").click(function(){ $("#relatedvod").load("/sys/load_index.php?id=54497"); $("#framepics").removeClass('bold'); $("#moviescenes").addClass('bold');});
$("#framepics").click(function(){ $("#relatedvod").load("/sys/load_pics.php?id=54497&t="); $("#moviescenes").removeClass('bold'); $("#framepics").addClass('bold');});
$("#myvod").click(function(){ $("#relatedvod").load("/sys/load_vod.php");});
$("#myscenes").click(function(){ $("#relatedvod").load("/sys/load_scenes.php");});

});</script>
<div id="navline" style="margin-top: 7px;">
<span id="oldest_movie" class="navlink blue" title="oldest">&lt;&lt;</span>
 <span id="prev_movie" class="navlink blue">previous</span>
 - <span id="next_movie" class="navlink blue bold">next movie</span>
 <span id="newest_movie" class="navlink blue" title="newest">>></span>
 &nbsp;&nbsp;#1,501 <a href="http://www.data18.com/studios/private/movies.html" style="color: #BA0F20;">Show All</a></div>
</div>
</div></div>
        </div><div style="clear: both;"></div><div style="float: left; width: 650px;"><div style="background: #DADADA; padding: 10px; margin-bottom: 8px; margin-top: 0px; width: 620px;
 border-top: 3px solid #B92525;"><div class="gen12" style="background: #FAFAD2; width: 591px; padding: 13px; 
 margin-bottom: 8px;">
<span class="gen bold">Membership</span>: Not available.
</div><div class="gen12" style="background: lightblue; width: 605px; height: 109px; padding: 8px;  margin-bottom: -3px;"><div style="vertical align: bottom;             
 margin-right: 10px;" class="gen11">
<p style="padding: 6px;">
<span class="gen bold">Video on Demand:</span> SD up to 480p &nbsp;* <i>Just pay for what you want</i> - Instant Access.
</p><p style="margin-left: 4px; margin-top: -3px; margin-bottom: 5px;"><b>Exclusive Online method</b> - Select your favourite option and start Watching Now!</p></div>
<div style="padding: 3px;"><div style="float: left; width: 5px;">
&nbsp;&nbsp;</div>
<div style="float: left; margin-right: 8px; background: #75ADF7; width: 125px; padding: 7px;
 border-radius:3px; -moz-border-radius:3px; -webkit-border-radius:3px;">
<div style="margin-bottom: 2px;">
<a href="https://secure.data18.com/store/54497/streaming/2days" style="text-decoration: none; color: black;" rel="nofollow"><b>Rental</b> Movie <span class="gen11"><u>2 days</u></span></a></div>
<a href="https://secure.data18.com/store/54497/streaming/2days" style="text-decoration: none; color: black;" rel="nofollow">&nbsp;<span style="font-size: 20px; color: white;">$3.99</span>&nbsp;&nbsp;
 <img src="http://img.data18.com/images/Play-16.png" width="10" height="10" alt="Streaming" />
</a>
</div>
<div style="float: left; margin-right: 8px; background: #75ADF7; width: 130px; padding: 7px;
 border-radius:3px; -moz-border-radius:3px; -webkit-border-radius:3px;">
<div style="margin-bottom: 2px;"><a href="https://secure.data18.com/store/54497/download_to_own" style="text-decoration: none; color: black;" rel="nofollow"><b>Buy</b> Full Movie</a></div>
<a href="https://secure.data18.com/store/54497/download_to_own" style="text-decoration: none; color: black;" rel="nofollow">&nbsp;<span style="font-size: 20px; color: white;">$16.99</span>&nbsp;&nbsp;
 <img src="http://img.data18.com/images/Play-16.png" width="10" height="10" alt="Streaming" />
 + <img src="http://img.data18.com/images/disk.png" width="10" height="10" alt="Download" /> 
</a>
</div><div style="float: left; background: #75ADF7; width: 122px; padding: 7px; margin-top: 0px; overflow: hidden;
 border-radius:3px; -moz-border-radius:3px; -webkit-border-radius:3px;">
<div style="margin-bottom: 2px;">Pay <b>per Minute</b>
 &nbsp;<img src="http://img.data18.com/images/Play-16.png" width="10" height="10" alt="Streaming" />
</div>

<p style="margin-top: 3px; margin-bottom: -1px;">
 <select name="forma" onchange="window.parent.parent.window.location = this.options[this.selectedIndex].value;"
 style="font-family:arial; font-size:9pt; width: 117px;">
<option value="#" selected="selected">Select Package</option>
<option value="https://secure.data18.com/store/54497/buy-15-minutes">15 minutes - $3.99</option>
<option value="https://secure.data18.com/store/54497/buy-30-minutes">30 minutes - $6.99</option>
<option value="https://secure.data18.com/store/54497/buy-45-minutes">45 minutes - $8.99</option>
<option value="https://secure.data18.com/store/54497/buy-60-minutes">60 minutes - $9.99</option>
<option value="https://secure.data18.com/store/54497/buy-120-minutes">120 minutes - $16.99</option>
<option value="https://secure.data18.com/store/54497/buy-240-minutes">240 minutes - $28.99</option>
<option value="https://secure.data18.com/store/54497/buy-360-minutes">360 minutes - $39.99</option>
<option value="https://secure.data18.com/store/54497/buy-480-minutes">480 minutes - $48.99</option>
<option value="https://secure.data18.com/store/54497/buy-960-minutes">960 minutes - $91.99</option>
<option value="https://secure.data18.com/store/54497/buy-2200-plus-100-minutes">* Super Packages :</option>
<option value="https://secure.data18.com/store/54497/buy-2200-plus-100-minutes">2200 minutes + 100 FREE - $199.99
</option>
<option value="https://secure.data18.com/store/54497/buy-3900-plus-200-minutes">3900 minutes + 200 FREE - $349.99
</option>
<option value="https://secure.data18.com/store/54497/buy-5800-plus-300-minutes">5800 minutes + 300 FREE - $499.99
</option>
</select>
</p>

</div><div style="clear: both;"></div>
</div></div></div></div><div style="float: left; width: 318px;"><div style="background: #F3F3F3; border-top: 3px solid grey; height: 15px; padding: 12px; margin-bottom: 8px;" class="gen12">
</div><div style="background: #DADADA; width: 302px; height: 105px; margin-bottom: 6px; padding: 8px;">
</div></div><div style="clear: both;"></div><div style="float: left; width: 650px;"><div style="background: #F3F3F3; width: 640px; padding: 0px; margin-bottom: 5px;"><div style="float: left; width: 230px; overflow: hidden; margin-left: 8px; margin-top: 8px; margin-bottom: 8px;"><a href="http://covers.data18.com/3/154497-the-private-life-of-jodie-moore-front-dvd.jpg" class="grouped_elements" rel="covers" title="The Private Life of Jodie Moore DVD Front Cover"><img src="http://img.data18.com/covers/private/private-life-of-jodie-moore.jpg" alt="Cover" class="noborder" width="230" /></a>

<p class="genmed p4 mt4">
Click Cover to Enlarge - <a href="http://covers.data18.com/3/154497-the-private-life-of-jodie-moore-back-dvd.jpg" class="grouped_elements" rel="covers" title="The Private Life of Jodie Moore DVD Back Cover">Back Cover</a>
</p>
</div><div style="float: left; width: 385px; margin-top: 8px;
 overflow: hidden; height: 392px;
 padding: 8px;" class="gen12"><p style="margin-top: 8px;">* <i>Compilation:</i> Selected scenes from different movies.</p><div style="height: 8px;"></div><p>Production Year: 2003 | Release date: September, 2003
</p><p><b>Studio:</b> <a href="http://www.data18.com/studios/private/">Private</a> | <b>Director:</b> Unknown</p><p class="gen12"><b>Description:</b><br />HARDCORE XXX SEX ACTION! 2-DISC COLLECTOR'S EDITION. Discover all of Jodie Moore's finest scenes for Private and find out her sexiest secrets! </p></div>
<div style="clear: both;"></div></div></div><div style="float: left; width: 318px;"><div style="margin-bottom: 6px; marin-left: 0px; margin-top: 0px;">
        <p style="background: #DADADA; margin: 0px; width: auto; padding: 6px;">
        <span class="gen" style="font-weight: bold;">Related Scenes:</span></p>
        </div><div style="background: grey; height: 175px; text-align: center; margin-bottom: 6px;" class="gen"><br /><br /><br /><br />

<b>Scene Index not Available</b>
</div><div style="margin-bottom: 5px; background: #f3f3f3; width: 318px; height: 200px;"></div></div>
<div style="clear: both;"></div><div style="float: left; width: 650px;"><div style="padding: 10px; margin-top: 15px;"><p><span class="gen" style="font-weight: bold;">Cast of The Private Life of Jodie Moore:</span> <span class="gen11">( In alphabetic order )</span></p>
        <div class="contenedor" style="overflow:auto; padding: 6px;">
        <div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/alberto_rey/"><img src="http://img.data18.com/images/no_prev_60.gif" class="yborder" alt="Alberto Rey" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/alberto_rey/" class="gensmall">Alberto Rey</a>
</p>
</div><div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/bobbi_eden/"><img src="http://img.data18.com/images/stars/60/237.jpg" class="yborder" alt="Bobbi Eden" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/bobbi_eden/" class="gensmall">Bobbi Eden</a>
</p>
</div><div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/elza_brown/"><img src="http://img.data18.com/images/no_prev_60.gif" class="yborder" alt="Elza Brown" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/elza_brown/" class="gensmall">Elza Brown</a>
</p>
</div><div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/jodie_moore/"><img src="http://img.data18.com/images/no_prev_60.gif" class="yborder" alt="Jodie Moore" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/jodie_moore/" class="gensmall">Jodie Moore</a>
</p>
</div><div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/mandy_bright/"><img src="http://img.data18.com/images/stars/60/1070.jpg" class="yborder" alt="Mandy Bright" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/mandy_bright/" class="gensmall">Mandy Bright</a>
</p>
</div><div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/philippe_dean/"><img src="http://img.data18.com/images/no_prev_60.gif" class="yborder" alt="Philippe Dean" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/philippe_dean/" class="gensmall">Philippe Dean</a>
</p>
</div><div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/sebastian_barrio/"><img src="http://img.data18.com/images/no_prev_60.gif" class="yborder" alt="Sebastian Barrio" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/sebastian_barrio/" class="gensmall">Sebastian Barrio</a>
</p>
</div><div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/tyce_bune/"><img src="http://img.data18.com/images/no_prev_60.gif" class="yborder" alt="Tyce Bune" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/tyce_bune/" class="gensmall">Tyce Bune</a>
</p>
</div>
        </div><p><b>More performers</b>: <a href="http://www.data18.com/dev/claudia_clair/">Claudia Clair</a></p></div></div>                
<div style="float: left; width: 318px;"><div style="margin-top: 20px;"><div style="background: #DADADA; margin: 0px; width: auto; margin-bottom: 3px; padding: 6px;">
<span class="gen" style="font-weight: bold;">Related Studio:</span>
</div>
<div style="padding: 5px; background: #F7F7F7;">
<div style="width: 308px; height: 70px; overflow: hidden;">
<div style="margin-top: -5px; margin-left: -5px;">
<a href="http://www.data18.com/studios/private/"><img src="http://img.data18.com/images/pic/private.jpg" alt="studio" /></a>
</div>
</div></div><div id="listpornstarsdiv" style="background: #F7F7F7; padding: 6px; margin-bottom: 5px;"><p class="gen12"><a href="http://www.data18.com/studios/private/movies.html" class="bold">Movies</a> <span class="genmed">1,501</span>&nbsp;&nbsp;<a href="http://www.data18.com/studios/private/content.html" class="bold">Scenes</a> <span class="genmed">6,504</span>&nbsp;&nbsp;<a href="http://www.data18.com/studios/private/with.html" class="bold">Pornstars</a> <span class="genmed">3,721</span>&nbsp;</p><form action="http://www.data18.com/connections/">  
<div style="margin-left: 6px; margin-top: 5px;">
<input type="text" name="v2" maxlength="256" style="background: #DADADA; width: 190px; font-size: 16px;"
 placeholder="movies, pornstars, ..."/>
 <input type="submit" value="Search" style="font-size: 13px;" />
<input type="hidden" name="v1" value="private" />
<input type="hidden" name="studioid" value="457" />
</div>
</form><div style="padding: 8px;"><b>About Private</b> 
 - Where & How:<br />
This studio offers different methods to Watch:
<p style="margin-left: 5px; margin-top: 5px;"><a href="http://www.data18.com/studios/private/membership.html">Official Membership</a> (887)</p><p style="margin-left: 5px;"><a href="http://www.data18.com/studios/private/dvd.html">DVD</a> (1397) & <a href="http://www.data18.com/studios/private/dvd.html/used">Used DVDs</a> (138) - <a href="http://www.data18.com/studios/private/blu-ray.html">Blu-Ray</a> (10)</p><p style="margin-left: 5px;"><a href="http://www.data18.com/studios/private/on-demand.html">Video on Demand</a> (1031)
 Own, Rental, x Minute</p><p style="margin-left: 5px;"><span class="red">New Option:</span> <a href="http://www.data18.com/studios/private/on-demand.html/scenes">Pay per Scene</a> 3719</p>
</div><div style="margin-left: 5px; margin-top: 3px; margin-bottom: 10px;" class="gen">
        <p style="font-weight: bold;" class="gen11">Performer Guide:</p>
        
<div id="starselectb">
<select style="width: 200px; padding: 3px;">
<option selected="selected">Search Pornstars...</option>
</select>
</div>
        </div><script>              
        $(document).ready(function(){
        $("#listpornstarsdiv").one("mouseover", function() {
	$("#movieselectb").load("/sys/related_movies.php?s=457");
	$("#starselectb").load("/sys/related_studio.php?s=457");
    });
        });
        </script></div></div></div>
<div style="clear: both;"></div><div style="height: 3px;"></div><div id="scenes"></div><div style="padding: 6px;"><div style="background: #FBFBFB; padding: 8px; margin-bottom: 3px;">
<p class="gen" style="font-weight: bold;">Scene Index:</p>
<p>Sorry, we don't have the scene index for now, but here you have free pictures/videostills from the movie.</p>
</div><a href="http://www.data18.com/viewer/654497/01"><img src="http://ima5.data18.com/pics/457/54497/th5/01.jpg"  alt="image 01" style="border: 15px solid #EEEEEE;" /></a> <a href="http://www.data18.com/viewer/654497/03"><img src="http://ima5.data18.com/pics/457/54497/th5/07.jpg"  alt="image 03" style="border: 15px solid #EEEEEE;" /></a> <a href="http://www.data18.com/viewer/654497/05"><img src="http://ima5.data18.com/pics/457/54497/th5/13.jpg"  alt="image 05" style="border: 15px solid #EEEEEE;" /></a> <a href="http://www.data18.com/viewer/654497/07"><img src="http://ima5.data18.com/pics/457/54497/th5/19.jpg"  alt="image 07" style="border: 15px solid #EEEEEE;" /></a> <a href="http://www.data18.com/viewer/654497/09"><img src="http://ima5.data18.com/pics/457/54497/th5/25.jpg"  alt="image 09" style="border: 15px solid #EEEEEE;" /></a> <a href="http://www.data18.com/viewer/654497/11"><img src="http://ima5.data18.com/pics/457/54497/th5/31.jpg"  alt="image 11" style="border: 15px solid #EEEEEE;" /></a> <a href="http://www.data18.com/viewer/654497/13"><img src="http://ima5.data18.com/pics/457/54497/th5/37.jpg"  alt="image 13" style="border: 15px solid #EEEEEE;" /></a> <a href="http://www.data18.com/viewer/654497/15"><img src="http://ima5.data18.com/pics/457/54497/th5/43.jpg"  alt="image 15" style="border: 15px solid #EEEEEE;" /></a> <a href="http://www.data18.com/viewer/654497/17"><img src="http://ima5.data18.com/pics/457/54497/th5/49.jpg"  alt="image 17" style="border: 15px solid #EEEEEE;" /></a> </div><div style="height: 50px;"></div><div style="width: 900px; padding: 8px; margin-bottom: 10px;">
<p><span class="big bold">18 U.S.C.Section 2257 Compliance Statement:</span></p>
<p class="gen12">All models were at least 18 years old when they were photographed &amp; shooted.</p><p class="gen12">
Information from our official store: <a href="http://www.data18.com/store/help/cs_2257" onclick="window.open(this.href, this.target, 'width=995,height=400,top=150,left=150'); return false;"  rel="nofollow">Click Here for 18 U.S.C. 2257 information </a></p></div></div><div style="clear: both;"></div><div style="height: 275px; background: #f3f3f3; margin-top: 3px; padding: 10px; text-align: center;"><div style="width: 310px; height: 72px; overflow: hidden; margin-bottom: 10px;">
<div style="margin-top: -4px; margin-left: -4px;">
<a href="http://www.data18.com/studios/private/"><img src="http://img.data18.com/images/pic/private.jpg" alt="studio" /></a>
</div>
</div><div style="float: left; padding: 8px;">
<a href="http://www.data18.com/movies/1157010"><img src="http://img.data18.com/covers/nav/7/1157010-tattoo-fever.jpg" style="width: 120px;" /></a>
</div> <div style="float: left; padding: 8px;">
<a href="http://www.data18.com/movies/1156821"><img src="http://img.data18.com/covers/nav/7/1156821-pajama-party.jpg" style="width: 120px;" /></a>
</div> <div style="float: left; padding: 8px;">
<a href="http://www.data18.com/movies/1156759"><img src="http://img.data18.com/covers/nav/7/1156759-mountain-crush-2-snowbunnies.jpg" style="width: 120px;" /></a>
</div> <div style="float: left; padding: 8px;">
<a href="http://www.data18.com/movies/1156757"><img src="http://img.data18.com/covers/nav/7/1156757-bachelorette-party.jpg" style="width: 120px;" /></a>
</div> <div style="float: left; padding: 8px;">
<a href="http://www.data18.com/movies/1156467"><img src="http://img.data18.com/covers/nav/7/1156467-cute-and-tight-holes-6.jpg" style="width: 120px;" /></a>
</div> <div style="float: left; padding: 8px;">
<a href="http://www.data18.com/movies/1156310"><img src="http://img.data18.com/covers/nav/7/1156310-anal-loving-teenagers-4.jpg" style="width: 120px;" /></a>
</div> <div style="float: left; padding: 8px;">
<a href="http://www.data18.com/movies/1155814"><img src="http://img.data18.com/covers/nav/7/1155814-double-lives.jpg" style="width: 120px;" /></a>
</div> <div style="clear: both;"></div></div><div class="lfoo"><div class="block auto">
<a href="http://www.data18.com/movies/154497#" rel="nofollow" onclick="javascript: window.scrollTo(0,0);" class="gen12 bold">Back to Top</a>
</div>
</div>
<div class="clear"></div>
<div class="dfoo1">
<p class="gen bold">About data18.com</p>
<p><a href="http://www.data18.com/sys/report.php" rel="nofollow" onclick="this.target='_blank'" class="bold">Contact Us</a> - <a href="http://www.data18.com/2257.html" rel="nofollow" onclick="this.target='_blank'" class="bold">18 U.S.C. 2257</a></p>
<p>Do you like data18? <a href="http://www.data18.com/share.html" rel="nofollow" class="bold" onclick="this.target='_blank'">Share us!</a></p>
<p>Follow us: <a href="http://www.data18.com/rss.html" class="red" rel="nofollow">RSS Feeds</a> - <a href="http://www.twitter.com/data18" class="blue" rel="nofollow" onclick="this.target='_blank'">Twitter</a> @data18</p>
<p>We support the use of filtering software which prevents minors from accessing inappropriate material: <a href="http://cyberpatrol.com" rel="nofollow" onclick="this.target='_blank'">CyberPatrol</a> | <a href="http://www.pandasecurity.com/about/social-responsibility/children-internet/" rel="nofollow" onclick="this.target='_blank'">Panda</a> | <a href="http://www.netnanny.com" rel="nofollow" onclick="this.target='_blank'">Net Nanny</a></p>
</div>
<div class="dfoo2">
<p><a href="http://www.data18.com/sitemap.html" class="gen bold">Sitemap</a></p>
<p>- <a href="http://www.data18.com/pornstars/">Pornstars</a></p>
<p>- <a href="http://www.data18.com/movies/">Movies</a> </p>
<p>- <a href="http://www.data18.com/studios/">Studios</a></p>
<p>- <a href="http://www.data18.com/content/">Content</a> </p>
<p>- <a href="http://www.data18.com/sites/">Sites &amp; Networks</a></p>
<p>- <a href="http://www.data18.com/awards/">Porn Awards</a></p>
</div>
<div class="dfoo3">
<p class="gen bold">About our Store:</p>
<p>Buy <a href="http://www.data18.com/movies/dvd.html" class="bold">DVDs</a>, <a href="http://www.data18.com/movies/blu-ray.html" class="bold">Blu-Ray</a>, <a href="http://www.data18.com/movies/vod.html" class="bold">Video on Demand</a> and <a href="http://www.data18.com/sex-toys/" class="bold">Sex Toys</a>.</p>
<p>The Store is provided by <a href="http://www.adultempirecash.com" rel="nofollow" onclick="this.target='_blank'">Empire Stores</a>:<br /><a href="http://www.data18.com/store/help/cs_2257" onclick="window.open(this.href, this.target, 'width=980,height=400,top=150,left=150'); return false;"  rel="nofollow">18 U.S.C. 2257</a> - <a href="http://www.data18.com/store/help/terms_of_use" onclick="window.open(this.href, this.target, 'width=980,height=600,top=150,left=150'); return false;"  rel="nofollow">Terms of Use</a> - <a href="http://www.data18.com/store/help/privacy_policy" onclick="window.open(this.href, this.target, 'width=980,height=600,top=150,left=150'); return false;"  rel="nofollow">Privacy Policy</a></p>
<p> Visit our store in "Full Mode", <a href="http://store.data18.com" rel="nofollow" onclick="this.target='_blank'">Click Here</a></p>
<p><span class="bold">Customer Service:</span> <a href="http://www.data18.com/store/help" rel="nofollow">Help Center</a> <a href="http://store.data18.com/account/inquiry" rel="nofollow" onclick="this.target='_blank'">Ask a Question</a> <a href="http://www.data18.com/store/help" rel="nofollow">Chat live</a></p>
<p><a href="http://www.data18.com/store/help/discreet_service" rel="nofollow">Discreet Service</a> - <a href="http://www.data18.com/store/help/shipping" rel="nofollow">Shipping Methods and Rates</a> - <a href="http://www.data18.com/store/help/return_policy" rel="nofollow">Return Policy</a>
</p>           
</div><div class="dsecure genmed">
<div class="bso spr-secure"></div>
<p>Transaction process is safe and customers' information is secure.</p>
<p>data18 encrypts confidential information with the Secure Sockets Layer (SSL)</p>
</div>
<div class="clear"></div>
</div>
</div>
<script type="text/javascript">
$(document).ready(function() {
$("a.grouped_elements").fancybox();
$("#searchform").focus();
});      


</script><div id="finalbody"></div>






</body>
</html>
    '''
    html3='''
    
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Picture Perfect Fuck (2016) - Porn Movie - data18.com</title>
<link rel="alternate" type="application/atom+xml" title="ALL Movies - New Releases" href="http://www.data18.com/rss/new-movies" />
<link rel="alternate" type="application/atom+xml" title="ALL Updates - New Releases" href="http://www.data18.com/rss/new-updates" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:site" content="@data18" />
<meta name="twitter:title" content="Picture Perfect Fuck (2016) - Porn Movie" />
<meta property="og:image" content="http://covers.data18.com/7/1153530-picture-perfect-fuck-front-dvd.jpg" />
<meta property="og:title" content="Picture Perfect Fuck (2016) - Porn Movie" />
<meta property="og:description" content="Victoria and Max's scenes are picture perfect and need no words. He's a photographer, she's a model and the attraction is smooth but instant. In this environment wonderfully void of context, they u..." />
<meta property="og:site_name" content="data18" />
<meta property="og:type" content="video.movie" />
<meta property="og:url" content="http://www.data18.com/movies/153530" />
<meta name="description" content="Victoria and Max's scenes are picture perfect and need no words. He's a photographer, she's a model and the attraction is smooth but instant. In this environment wonderfully void of context, they u..." />
<meta name="keywords" content="picture perfect fuck" />
<meta name="RATING" content="RTA-5042-1996-1400-1577-RTA" />
<link rel="stylesheet" href="http://www.data18.com/css/general.css" type="text/css" media="screen" />


<link rel="shortcut icon" href="http://www.data18.com/fav.ico" />
<script type="text/javascript">
  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-18866535-1']); 
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);      
  })();
</script>

<script src="http://www.data18.com/js/jquery-1.11.0.min.js"></script>
<script src="http://www.data18.com/js/jquery.lazyload.js"></script>
<script src="http://www.data18.com/js/feather.js"></script>
<script src="http://www.data18.com/js/tooltipster.bundle.min.js"></script>


    <script>
        $(document).ready(function() {

$('.tooltip').tooltipster({
theme: 'tooltipster-noir',
maxWidth: 290
});

        });
    </script>

<script>
        $(document).ready(function(){
        $("#listpornstarsdiv").one("click, mouseover", function() {
        $("#listpornstars").load("/sys/related_site3.php?s=2943");   
    });
        });
        </script><script type="text/javascript" src="http://www.data18.com/js/jquery.fancybox.js?v=2.1.5"></script>
<script>
$(document).ready(function(){
$('#nav_movies').on('change', function() {
$("#navline").load("/sys/c_movies.php?mode=&m=153530&v="+this.value+"");
});
});
</script>
</head>
<body>
<div class="main gre1"><div id="centered" class="main2"><div class="lineup"></div><div style="background:white;padding:10px;"><div style="float: left; width: 160px; height: 66px; overflow: hidden;
 margin-top: -2px;">
<span class="red bold">Store</span>            
 &amp; <span class="red bold">Porn Database</span>

<div style="margin-top: 1px;">
<a href="http://www.data18.com"><img src="http://img.data18.com/images/logo-mini.jpg" alt="logo" /></a></div></div><div style="float: left; width: 785px; height: 60px;" class="p3"><p style="margin: 0px; width: 805px; margin-left: 0px; margin-top: -3px;">By method: <span style="background: LightGoldenRodYellow;; color: black; padding: 5px;" class="bordat"><a href="http://www.data18.com/movies/membership.html" style="text-decoration: none; color: black;">Membership</a></span>
 <span style="background: #b4d9ff; color: black; padding: 5px;" class="bordat"><a href="http://www.data18.com/movies/vod.html/pps" style="text-decoration: none; color: black;">Pay per scene</a></span>
 <span style="background: #b4d9ff; color: black; padding: 5px;" class="bordat"><a href="http://www.data18.com/movies/vod.html/own" style="text-decoration: none; color: black;">Digital Own</a></span>
 <span style="background: #b4d9ff; color: black; padding: 5px;" class="bordat"><a href="http://www.data18.com/movies/vod.html/rental" style="text-decoration: none; color: black;">Rental Movie</a></span>
 <span style="background: #b4d9ff; color: black; padding: 5px;" class="bordat"><a href="http://www.data18.com/movies/vod.html/ppm" style="text-decoration: none; color: black;">Pay per Minute</a></span>
 <span style="background: #E5E5E5; color: black; padding: 5px;" class="bordat"><a href="http://www.data18.com/movies/dvd.html" style="text-decoration: none; color: black;">DVD</a></span>
 <span style="background: #E5E5E5; color: black; padding: 5px;" class="bordat"><a href="http://www.data18.com/movies/blu-ray.html" style="text-decoration: none; color: black;">Blu-Ray</a></span></p><div style="width: 805px; margin-top: 13px; margin-bottom: -7px; margin-left: 3px;"><a href="http://www.data18.com/pornstars/" style="text-decoration: none;">
<div style="float: left; background: #DADADA; padding: 8px; margin-right: 5px;" class="bordat"
 onmouseover="this.style.background='#f0f0f0'" onmouseout="this.style.background='#DADADA'">
<span class="gen bold">Pornstars</span><br /><span class="genmed">12,670</span>
</div>
</a>

<a href="http://www.data18.com/movies/" style="text-decoration: none;">
<div style="float: left; background: #DADADA; padding: 8px; margin-right: 5px;" class="bordat"
 onmouseover="this.style.background='#f0f0f0'" onmouseout="this.style.background='#DADADA'">
<span class="gen bold">Movies</span><br /><span class="genmed">145,605</span>
</div>
</a>

<a href="http://www.data18.com/content/" style="text-decoration: none;">
<div style="float: left; background: #DADADA; padding: 8px; margin-right: 5px;" class="bordat"
 onmouseover="this.style.background='#f0f0f0'" onmouseout="this.style.background='#DADADA'">
<span class="gen bold">Scene Guide</span>  
<br /><span class="genmed">572,784 Scenes & Galleries</span>
</div>
</a>

<a href="http://www.data18.com/studios/" style="text-decoration: none;">
<div style="float: left; background: #DADADA; padding: 8px; margin-right: 5px;" class="bordat"
 onmouseover="this.style.background='#f0f0f0'" onmouseout="this.style.background='#DADADA'">
<span class="gen bold">Studios</span>
<br /><span class="genmed">1,357</span>
</div>  
</a>

<a href="http://www.data18.com/sites/" style="text-decoration: none;">
<div style="float: left; background: #DADADA; padding: 8px; margin-right: 5px;" class="bordat"
 onmouseover="this.style.background='#f0f0f0'" onmouseout="this.style.background='#DADADA'">
<span class="gen bold">Paysites</span>
<br /><span class="genmed">813</span>
</div>
</a><div style="clear: both;"></div>
</div>
</div><div style="clear: both;"></div></div><div class="lineup"></div><div style="background: #e6e6e6; width: 100%; height: 50px;">
<div style="float: left; margin-top: 3px; width: 480px; padding: 10px;">
<form action="http://www.data18.com/search/">
 &nbsp;<input id="searchform" type="text" name="k" class="form3" style="background: tranparent; font-size: 16px;"
 placeholder="Find pornstars, movies, scenes, ..." autofocus="autofocus"  />
 <input type="submit" class="gen" value="Search" />
 &nbsp;<a href="http://www.data18.com/search/">Advanced Search</a>
</form>
</div><div style="float: left; margin-top: 3px; width: 450px;padding: 10px;" class="gen11">
<form action="http://www.data18.com/connections/" method="get">
 Connections:
<input type="text" name="v1" size="22" value="" placeholder="Variable 1" class="form2"
 style="font-size: 16px;" />
 &nbsp;and&nbsp;                  
 <input type="text" name="v2" size="22" value="" placeholder="Variable 2" class="form2"
 style="font-size: 16px;" />
 <input type="submit" class="gen" value="Go" />
 <input type="hidden" name="ref" value="1" />
</form>
</div><div style="clear: both;"></div>
</div><div style="background: width: 100%;">
<p style="padding: 8px; vertical-align: middle;" class="gen12"><img src="http://img.data18.com/images/user-16.png"
 style="width: 16px; height: 16px;" alt="user" />
 &nbsp;<a href="#" data-featherlight="http://www.data18.com/sys/box-login.php" class="bold">Sign In</a>
 - <a href="#" data-featherlight="http://www.data18.com/sys/box-register.php" class="bold">Create a New Account</a>
&nbsp;&nbsp; &nbsp;<select name="forma" onchange="window.parent.parent.window.location = this.options[this.selectedIndex].value;" 
 style="margin-top: 4px;  font-family:arial; font-size:9pt; width: 100px;">
<option value="https://secure.data18.com/store/buy-60-minutes" selected="selected">Buy Minutes</option>
<option value="https://secure.data18.com/store/buy-60-minutes">Select Package:</option>
<option value="https://secure.data18.com/store/buy-15-minutes">15 minutes - $3.99</option>
<option value="https://secure.data18.com/store/buy-30-minutes">30 minutes - $6.99</option>
<option value="https://secure.data18.com/store/buy-45-minutes">45 minutes - $8.99</option>
<option value="https://secure.data18.com/store/buy-60-minutes">60 minutes - $9.99</option>
<option value="https://secure.data18.com/store/buy-120-minutes">120 minutes - $16.99</option>
<option value="https://secure.data18.com/store/buy-240-minutes">240 minutes - $28.99</option>
<option value="https://secure.data18.com/store/buy-360-minutes">360 minutes - $39.99</option>
<option value="https://secure.data18.com/store/buy-480-minutes">480 minutes - $48.99</option>
<option value="https://secure.data18.com/store/buy-960-minutes">960 minutes - $91.99</option>
<option value="https://secure.data18.com/store/buy-2200-plus-100-minutes">* Super Packages :</option>
<option value="https://secure.data18.com/store/buy-2200-plus-100-minutes">2200 minutes + 100 FREE - $199.99</option>  
<option value="https://secure.data18.com/store/buy-3900-plus-200-minutes">3900 minutes + 200 FREE - $349.99</option>
<option value="https://secure.data18.com/store/buy-5800-plus-300-minutes">5800 minutes + 300 FREE - $499.99</option>
</select>&nbsp;&nbsp;<a href="http://www.data18.com/store/ppm-how-it-works" onclick="window.open(this.href, this.target, 'width=850,height=550,top=150,left=150'); return false;" class="gen11" rel="nofollow">How it Works?</a> &nbsp;&nbsp; &nbsp;&nbsp; <a href="http://www.data18.com/store/cart-check">Cart: 0 items</a></p>
</div><div style="float: left; width: 745px;">
<div class="p8 dloc">
<a href="http://www.data18.com" class="red bold" rel="nofollow">data18</a>
 > <a href="http://www.data18.com/movies/" class="bold">Movies</a> > <a href="http://www.data18.com/sites/21naturals/">21naturals</a> <i>Site</i> 
</div>
</div>

<div style="float: left; width: 235px;">
<div class="p8 dloc" style="text-align: right;">
 
 <a href="https://twitter.com/intent/tweet?status=Picture%20Perfect%20Fuck%20(2016)%20-%20Porn%20Movie%20http%3A%2F%2Fwww.data18.com%2Fmovies%2F1153530%20via%20@data18" onclick="window.open(this.href, this.target, 'width=500,height=400, top=150,left=150'); return false;" class="bso spr-twitter block mr5" rel="nofollow"></a> 
 <a href="http://www.addtoany.com/share_save#url=http%3A%2F%2Fwww.data18.com%2Fmovies%2F1153530&amp;title=Picture%20Perfect%20Fuck%20(2016)%20-%20Porn%20Movie" onclick="window.open(this.href, this.target, 'width=700,height=600, top=150,left=150'); return false;" class="bso spr-plus block mr5" rel="nofollow"></a>
 <a href="http://www.addtoany.com/share_save#url=http%3A%2F%2Fwww.data18.com%2Fmovies%2F1153530&amp;title=Picture%20Perfect%20Fuck%20(2016)%20-%20Porn%20Movie" onclick="window.open(this.href, this.target, 'width=700,height=600, top=150,left=150'); return false;" class="block mt2 mr5" rel="nofollow"><span style="color: black;">Share this Movie</span></a>

</div>
</div>
<div style="clear: both;"></div>
<div style="background: white;" class="p8"><div style="float: left; width: 648px; height: 55px; overflow: hidden;">
<h1 style="height: 23px; overflow: hidden; font-size: 18px; margin: 3px;">Picture Perfect Fuck</h1>
</div><div style="float: left; width: 312px; height: 57px; border-bottom: 4px solid white;
 margin-top: -8px;
 background: #e6e6e6;" class="p4">
	<div style="margin-top: 10px; margin-left: 10px;"><div id="navmovies" style="width: 310px; height: 41px; overflow: hidden;">
<div style="padding: 0px; margin-bottom: 7px; font-size: 11px;">
<b>Nav:</b>&nbsp;
 <select id="nav_movies" style="width: 160px; font-size: 12px;">               
<option value="4-1509" >21naturals [site]</option><option value="3-25445">Jakub Forman [star]</option>
<option value="3-25487">Mona Kim [star]</option>
<option value="3-25411">Mr Clark [star]</option>
<option value="3-18087">Renato [star]</option>
<option value="3-22697">Tina Kay [star]</option>
<option value="3-24929">Victoria Daniels [star]</option>

</select>
<script>$(document).ready(function(){



$("#next_movie").click(function(){ window.location = 'http://www.data18.com/go/next_movie/4/1509/153530'; });
$("#prev_movie").click(function(){ window.location = 'http://www.data18.com/go/prev_movie/4/1509/153530'; });
$("#oldest_movie").click(function(){ window.location = 'http://www.data18.com/go/oldest_movie/4/1509/153530'; });
$("#newest_movie").click(function(){ window.location = 'http://www.data18.com/go/newest_movie/4/1509/153530'; });
$("#bigplayer").click(function(){ window.location = 'http://www.data18.com/sys/big.php?url=/movies/1153530'; });
$("#moviescenes").click(function(){ $("#relatedvod").load("/sys/load_index.php?id=153530"); $("#framepics").removeClass('bold'); $("#moviescenes").addClass('bold');});
$("#framepics").click(function(){ $("#relatedvod").load("/sys/load_pics.php?id=153530&t="); $("#moviescenes").removeClass('bold'); $("#framepics").addClass('bold');});
$("#myvod").click(function(){ $("#relatedvod").load("/sys/load_vod.php");});
$("#myscenes").click(function(){ $("#relatedvod").load("/sys/load_scenes.php");});

});</script>
<div id="navline" style="margin-top: 7px;">
<span id="oldest_movie" class="navlink blue" title="oldest">&lt;&lt;</span>
 <span id="prev_movie" class="navlink blue">previous</span>
 - <span id="next_movie" class="navlink blue bold">next movie</span>
 <span id="newest_movie" class="navlink blue" title="newest">>></span>
 &nbsp;&nbsp;#9 <a href="http://www.data18.com/sites/21naturals/movies.html" style="color: #BA0F20;">Show All</a></div>
</div>
</div></div>
        </div><div style="clear: both;"></div><div style="float: left; width: 650px;"><div style="background: #DADADA; padding: 10px; margin-bottom: 8px; margin-top: 0px; width: 620px;
 border-top: 3px solid #B92525;"><div class="gen12" style="background: LightGoldenRodYellow; width: 601px; height: 65px; overflow: hidden;padding: 10px;">
<div style="float: left;">
<p><span class="gen bold">Membership: <u>21naturals</u></span></p>

	<p class="gen11" style="margin-top: -3px;">- Over 588 scenes, including this movie<br />- Unlimited Streaming & Downloads<br />- <b>HD Included</b> - Instant Access
	

</div>       
<div style="float: left; padding: 6px; margin-top: 0px; margin-left: 25px;">
<div style="margin-right: 8px; background: Gold; margin-top: -3px; width: 280px; height: 45px;  padding: 7px; text-align: center; cursor: pointer;" class="bordat">
<p><a href="http://www.data18.com/go/2943" rel="nofollow" style="color: black;" class="big bold" onclick="this.target='_blank'">Join 21naturals</a></p>
<span class="genmed">* Secure & Confidential. Easy cancel any time.</span>
</div>
</div>

<div style="clear: both;"></div>



</div><div class="gen12" style="background: lightblue; width: 605px; height: 90px; padding: 8px; margin-top: 8px; margin-bottom: -3px;"><div style="vertical align: bottom;             
 margin-right: 10px;" class="gen11">
<p style="padding: 6px;">
<span class="gen bold">Video on Demand:</span> <span class="gen11 blue bold">Full HD 1080p</span> &nbsp;* <i>Just pay for what you want</i> - Instant Access.
</p></div>
<div style="padding: 3px;"><div style="float: left; margin-right: 8px; background: #75ADF7; width: 140px; padding: 7px;
 border-radius:3px; -moz-border-radius:3px; -webkit-border-radius:3px;">
<div style="margin-bottom: 2px; margin-left: 2px;">
<a href="http://www.data18.com/movies/1153530#scenes" style="color: black; text-decoration: none; color: black;">Pay <b>per Scene</b></a>
 &nbsp;<a href="http://www.data18.com/movies/1153530#scenes" class="gen11 blue">Select</a></div>
&nbsp;<a href="http://www.data18.com/movies/1153530#scenes" style="color: black; text-decoration: none; color: black;"><span style="font-size: 20px; color: white;">$5.99</span>&nbsp;&nbsp;
 <img src="http://img.data18.com/images/Play-16.png" width="10" height="10" alt="Streaming" />
 + <img src="http://img.data18.com/images/disk.png" width="10" height="10" alt="Download" /> 
</a></div>
<div style="float: left; margin-right: 8px; background: #75ADF7; width: 125px; padding: 7px;
 border-radius:3px; -moz-border-radius:3px; -webkit-border-radius:3px;">
<div style="margin-bottom: 2px;">
<a href="https://secure.data18.com/store/153530/streaming/2days_hd" style="text-decoration: none; color: black;" rel="nofollow"><b>Rental</b> Movie <span class="gen11"><u>2 days</u></span></a></div>
<a href="https://secure.data18.com/store/153530/streaming/2days_hd" style="text-decoration: none; color: black;" rel="nofollow">&nbsp;<span style="font-size: 20px; color: white;">$5.99</span>&nbsp;&nbsp;
 <img src="http://img.data18.com/images/Play-16.png" width="10" height="10" alt="Streaming" />
</a>
</div>
<div style="float: left; margin-right: 8px; background: #75ADF7; width: 130px; padding: 7px;
 border-radius:3px; -moz-border-radius:3px; -webkit-border-radius:3px;">
<div style="margin-bottom: 2px;"><a href="https://secure.data18.com/store/153530/download_to_own_hd" style="text-decoration: none; color: black;" rel="nofollow"><b>Buy</b> Full Movie</a></div>
<a href="https://secure.data18.com/store/153530/download_to_own_hd" style="text-decoration: none; color: black;" rel="nofollow">&nbsp;<span style="font-size: 20px; color: white;">$21.99</span>&nbsp;&nbsp;
 <img src="http://img.data18.com/images/Play-16.png" width="10" height="10" alt="Streaming" />
 + <img src="http://img.data18.com/images/disk.png" width="10" height="10" alt="Download" /> 
</a>
</div><div style="float: left; background: #75ADF7; width: 122px; padding: 7px; margin-top: 0px; overflow: hidden;
 border-radius:3px; -moz-border-radius:3px; -webkit-border-radius:3px;">
<div style="margin-bottom: 2px;">Pay <b>per Minute</b>
 &nbsp;<img src="http://img.data18.com/images/Play-16.png" width="10" height="10" alt="Streaming" />
</div>

<p style="margin-top: 3px; margin-bottom: -1px;">
 <select name="forma" onchange="window.parent.parent.window.location = this.options[this.selectedIndex].value;"
 style="font-family:arial; font-size:9pt; width: 117px;">
<option value="#" selected="selected">Select Package</option>
<option value="https://secure.data18.com/store/153530/buy-15-minutes">15 minutes - $3.99</option>
<option value="https://secure.data18.com/store/153530/buy-30-minutes">30 minutes - $6.99</option>
<option value="https://secure.data18.com/store/153530/buy-45-minutes">45 minutes - $8.99</option>
<option value="https://secure.data18.com/store/153530/buy-60-minutes">60 minutes - $9.99</option>
<option value="https://secure.data18.com/store/153530/buy-120-minutes">120 minutes - $16.99</option>
<option value="https://secure.data18.com/store/153530/buy-240-minutes">240 minutes - $28.99</option>
<option value="https://secure.data18.com/store/153530/buy-360-minutes">360 minutes - $39.99</option>
<option value="https://secure.data18.com/store/153530/buy-480-minutes">480 minutes - $48.99</option>
<option value="https://secure.data18.com/store/153530/buy-960-minutes">960 minutes - $91.99</option>
<option value="https://secure.data18.com/store/153530/buy-2200-plus-100-minutes">* Super Packages :</option>
<option value="https://secure.data18.com/store/153530/buy-2200-plus-100-minutes">2200 minutes + 100 FREE - $199.99
</option>
<option value="https://secure.data18.com/store/153530/buy-3900-plus-200-minutes">3900 minutes + 200 FREE - $349.99
</option>
<option value="https://secure.data18.com/store/153530/buy-5800-plus-300-minutes">5800 minutes + 300 FREE - $499.99
</option>
</select>
</p>

</div><div style="clear: both;"></div>
</div></div></div></div><div style="float: left; width: 318px;"><div style="background: #F3F3F3; border-top: 3px solid grey; height: 15px; padding: 12px; margin-bottom: 8px;" class="gen12">
</div><div style="background: #DADADA; width: 302px; height: 153px; overflow: hidden; margin-bottom: 6px; padding: 8px;">
<p class="gen11" style="margin-bottom: 5px;"><b>Physical Format:</b>
 Pay w/ Credit Card - Paypal<br />
Discreet & Fast Shipping. We deliver woldwide.</p>
<div style="background: #F3F3F3; min-height: 79px; margin: 3px;">
<div style="float: left; width: 60px;">
<img src="http://img.data18.com/images/border-dvd.jpg" alt="dvd" /><p class="gensmall">&nbsp;1 disc</p></div>



<div style="float: left; width: 220px; overflow: hidden; padding: 5px;">
<p class="gen11">ID: 1883944 - UPC: 895152035068</p>

<p>
<a href="https://secure.data18.com/store/cart/dvd/1153530" rel="nofollow"
 style="font-size: 15px; font-weight: bold;" class="button">BUY DVD - $24.99</a>
</p>



<p><span style="color: green;" class="bold">In Stock</span> - Ships Immediately</p>


</div>

<div style="clear: both;"></div>

</div></div></div><div style="clear: both;"></div><div style="float: left; width: 650px;"><div style="background: #F3F3F3; width: 640px; padding: 0px; margin-bottom: 5px;"><div style="float: left; width: 230px; overflow: hidden; margin-left: 8px; margin-top: 8px; margin-bottom: 8px;"><a href="http://covers.data18.com/7/1153530-picture-perfect-fuck-front-dvd.jpg" class="grouped_elements" rel="covers" title="Picture Perfect Fuck DVD Front Cover"><img src="http://img.data18.com/covers/21naturals/picture-perfect-fuck.jpg" alt="Cover" class="noborder" width="230" /></a>

<p class="genmed p4 mt4">
Click Cover to Enlarge - <a href="http://covers.data18.com/7/1153530-picture-perfect-fuck-back-dvd.jpg" class="grouped_elements" rel="covers" title="Picture Perfect Fuck DVD Back Cover">Back Cover</a>
</p>
</div><div style="float: left; width: 385px; margin-top: 8px;
 overflow: hidden; height: 392px;
 padding: 8px;" class="gen12"><div style="float: left; background: #DADADA; margin-top: 0px; font-size: 15px; margin-left: 3px;" class="p8 mt5">
 <a href="http://www.data18.com/movies/trailers.html/1153530" style="color: black; font-size: 18px;">Play Trailer</a>
</div><div style="clear: both;"></div><div style="height: 8px;"></div><p>Production Year: 2016 | Release date: December, 2016
</p><p><b>Site:</b> <a href="http://www.data18.com/sites/21naturals/">21naturals</a> | <b>Director:</b> Unknown</p><p><b>Movie Length</b>: 87 min. in <a href="http://www.data18.com/movies/1153530#scenes">4 Scenes</a></p><p>
<b>Categories:</b> <span class="gensmall">General:</span> <a href="http://www.data18.com/movies/teen.html">Teen</a> <span class="gensmall">+18</span>, <span class="gensmall">How&nbsp;many:</span> <a href="http://www.data18.com/movies/couples.html">Couples</a>
</p><p class="gen12"><b>Description:</b><br />Victoria and Max's scenes are picture perfect and need no words. He's a photographer, she's a model and the attraction is smooth but instant. In this environment wonderfully void of context, they undress to fuck with all the lights on. Eveline gets her headphones on and tunes in to her favorite music. What better to get in the mood with her man? She feels sexy and she looks it too! They give it a whirl on the couch, royally bathed in white light. Eveline's soft body gently submits to Renato's hard erection. He comes in her open mouth while she heartily masturbates. Mona is in the condo by the tall windows getting all hot and bothered in anticipation for Max to show up. The lad comes in not a moment too soon and starts fingering the aroused brunette. Her sleek figure glows in the light, and their soft rhythms take them to the peak of their...</p></div>
<div style="clear: both;"></div></div></div><div style="float: left; width: 318px;"><div id="related"><div style="margin-bottom: 4px; margin-left: 0px;
 margin-left: 0px; margin-top: px;">
<div style="background: #E5E5E5; margin: 0px; width: px; padding: 6px;"
 onmouseover="this.style.background='#cfcfcf'" onmouseout="this.style.background='#E6E6E6'">
<a href="http://www.data18.com/movies/1153530#scenes" style="text-decoration: none; color: black;">
<div style="padding: 6px;">
<span class="gen" style="font-weight: bold;">Related Scenes [4]</span>
 <span id="gotoscene"></span><p style="margin-top: 2px;"><u>Go to Scene Index</u> for detailed information.</p>
</div>
</a></div></div><div  style="width: px;"><a href="http://www.data18.com/content/1162491" style="text-decoration: none; color: black;" title="A Picture Perfect Fuck">
<div class="gray2" style="margin-bottom: 5px; background: #f3f3f3; width: 294; height: 70px; overflow: hidden;" onmouseover="this.style.background='#F6F4D0'" onmouseout="this.style.background='#f3f3f3'">
                <div style="float: left; width: 125px; height:65px; overflow: hidden;"><img src="http://ima1.data18.com/329/2943/162491/hor5.jpg" class=""  alt="scene" /></div>
                <div style="float: left; width: 170px; padding: 6px;  margin-left: 3px;
 margin-top: 2px;"><b>Scene 1</b></a>&nbsp; <a href="https://secure.data18.com/store/scene/479012" rel="nofollow"
 style="text-decoration: none; background-color: #b4d9ff; color: black; padding: 3px;" class="gen11"><b>Buy Scene</b> $5.99</a>
<a href="http://www.data18.com/content/1162491" style="text-decoration: none; color: black;" title="A Picture Perfect Fuck"><p style="margin-top: 2px;">Victoria Daniels, Jakub Forman</p></div>
                <div style="clear: both;"></div></div></a><a href="http://www.data18.com/content/1162490" style="text-decoration: none; color: black;" title="Tuning Into Carnal">
<div class="gray2" style="margin-bottom: 5px; background: #DADADA; width: 294; height: 70px; overflow: hidden;" onmouseover="this.style.background='#F6F4D0'" onmouseout="this.style.background='#DADADA'">
                <div style="float: left; width: 125px; height:65px; overflow: hidden;"><img src="http://ima1.data18.com/329/2943/162490/hor5.jpg" class=""  alt="scene" /></div>
                <div style="float: left; width: 170px; padding: 6px;  margin-left: 3px;
 margin-top: 2px;"><b>Scene 2</b></a>&nbsp; <a href="https://secure.data18.com/store/scene/479013" rel="nofollow"
 style="text-decoration: none; background-color: #b4d9ff; color: black; padding: 3px;" class="gen11"><b>Buy Scene</b> $5.99</a>
<a href="http://www.data18.com/content/1162490" style="text-decoration: none; color: black;" title="Tuning Into Carnal"><p style="margin-top: 2px;">Eveline Dellai, Renato</p></div>
                <div style="clear: both;"></div></div></a><a href="http://www.data18.com/content/1162487" style="text-decoration: none; color: black;" title="Mona By The Tall Windows">
<div class="gray2" style="margin-bottom: 5px; background: #f3f3f3; width: 294; height: 70px; overflow: hidden;" onmouseover="this.style.background='#F6F4D0'" onmouseout="this.style.background='#f3f3f3'">
                <div style="float: left; width: 125px; height:65px; overflow: hidden;"><img src="http://ima1.data18.com/329/2943/162487/hor5.jpg" class=""  alt="scene" /></div>
                <div style="float: left; width: 170px; padding: 6px;  margin-left: 3px;
 margin-top: 2px;"><b>Scene 3</b></a>&nbsp; <a href="https://secure.data18.com/store/scene/479014" rel="nofollow"
 style="text-decoration: none; background-color: #b4d9ff; color: black; padding: 3px;" class="gen11"><b>Buy Scene</b> $5.99</a>
<a href="http://www.data18.com/content/1162487" style="text-decoration: none; color: black;" title="Mona By The Tall Windows"><p style="margin-top: 2px;">Mona Kim, Jakub Forman</p></div>
                <div style="clear: both;"></div></div></a><a href="http://www.data18.com/content/1162480" style="text-decoration: none; color: black;" title="Tender Tina Grinning">
<div class="gray2" style="background: #DADADA; width: 294; height: 70px; overflow: hidden;" onmouseover="this.style.background='#F6F4D0'" onmouseout="this.style.background='#DADADA'">
                <div style="float: left; width: 125px; height:65px; overflow: hidden;"><img src="http://ima1.data18.com/329/2943/162480/hor5.jpg" class=""  alt="scene" /></div>
                <div style="float: left; width: 170px; padding: 6px;  margin-left: 3px;
 margin-top: 2px;"><b>Scene 4</b></a>&nbsp; <a href="https://secure.data18.com/store/scene/479015" rel="nofollow"
 style="text-decoration: none; background-color: #b4d9ff; color: black; padding: 3px;" class="gen11"><b>Buy Scene</b> $5.99</a>
<a href="http://www.data18.com/content/1162480" style="text-decoration: none; color: black;" title="Tender Tina Grinning"><p style="margin-top: 2px;">Tina Kay, Clark</p></div>
                <div style="clear: both;"></div></div></a></div></div><div style="margin-bottom: 5px; background: #f3f3f3; width: 320px; height:50px;"></div></div>
<div style="clear: both;"></div><div style="float: left; width: 650px;"><div style="padding: 10px; margin-top: 15px;"><p><span class="gen" style="font-weight: bold;">Cast of Picture Perfect Fuck:</span> <span class="gen11">( In alphabetic order )</span></p>
        <div class="contenedor" style="overflow:auto; padding: 6px;">
        <div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/jakub_forman/"><img src="http://img.data18.com/images/stars/60/25445.jpg" class="yborder" alt="Jakub Forman" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/jakub_forman/" class="gensmall">Jakub Forman</a>
</p>
</div><div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/mona_kim/"><img src="http://img.data18.com/images/no_prev_60.gif" class="yborder" alt="Mona Kim" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/mona_kim/" class="gensmall">Mona Kim</a>
</p>
</div><div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/mr_clark/"><img src="http://img.data18.com/images/no_prev_60.gif" class="yborder" alt="Mr Clark" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/mr_clark/" class="gensmall">Mr Clark</a>
</p>
</div><div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/renato/"><img src="http://img.data18.com/images/stars/60/18087.jpg" class="yborder" alt="Renato" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/renato/" class="gensmall">Renato</a>
</p>
</div><div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/tina_kay/"><img src="http://img.data18.com/images/stars/60/22697.jpg" class="yborder" alt="Tina Kay" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/tina_kay/" class="gensmall">Tina Kay</a>
</p>
</div><div style="width: 75px;">
<p class="line1">
<a href="http://www.data18.com/victoria_daniels/"><img src="http://img.data18.com/images/stars/60/24929.jpg" class="yborder" alt="Victoria Daniels" /></a>
</p>
<p class="line1" style="align: center;">              
<a href="http://www.data18.com/victoria_daniels/" class="gensmall">Victoria Daniels</a>
</p>
</div>
        </div><p><b>More performers</b>: <a href="http://www.data18.com/dev/clark/">Clark</a>, <a href="http://www.data18.com/dev/eveline_dellai/">Eveline Dellai</a></p></div></div>                
<div style="float: left; width: 318px;"><div style="margin-top: 20px;"><div style="background: #DADADA; margin: 0px; width: auto; margin-bottom: 3px; padding: 6px;">
<span class="gen" style="font-weight: bold;">Related Site:</span>
</div>
<div style="padding: 5px; background: #F7F7F7;">
<div style="width: 308px; height: 70px; overflow: hidden;">
<div style="margin-top: -5px; margin-left: -5px;">
<a href="http://www.data18.com/sites/21naturals/"><img src="http://img.data18.com/images/pic/21naturals.jpg" alt="site" /></a>
</div>
</div>
</div><div id="listpornstarsdiv" style="background: #F7F7F7; padding: 6px; margin-bottom: 5px;"><p class="gen12"><a href="http://www.data18.com/sites/21naturals/content.html" class="bold">Scenes</a> <span class="genmed">588</span>&nbsp;&nbsp;&nbsp;<a href="http://www.data18.com/sites/21naturals/with.html" class="bold">Pornstars</a> <span class="genmed">259</span>&nbsp;&nbsp;&nbsp;<a href="http://www.data18.com/sites/21naturals/movies.html" class="bold">Movies</a> <span class="genmed">9</span></p><form action="http://www.data18.com/connections/">  
<div style="margin-left: 6px; margin-top: 5px;">
<input type="text" name="v2" maxlength="256" style="background: #DADADA; width: 190px; font-size: 16px;"
 placeholder="pornstars, movies, ..."/>
 <input type="submit" value="Search" style="font-size: 13px;" />
<input type="hidden" name="v1" value="21naturals" />
<input type="hidden" name="studioid" value="1509" />
</div>
</form><div style="padding: 8px;"><b>About 21naturals</b>
 - Where & How:<br />- All scenes are available on membership option.
<br />- This Studio sells part of his content (7%) on <a href="http://www.data18.com/sites/21naturals/dvd.html">Movies</a> (9) offering different methods to watch:<p style="margin-left: 5px; margin-top: 5px;"><a href="http://www.data18.com/sites/21naturals/dvd.html">DVD</a> (9) & <a href="http://www.data18.com/sites/21naturals/dvd.html/used">Used DVDs</a> (2)</p><p style="margin-left: 5px;"><a href="http://www.data18.com/sites/21naturals/on-demand.html">Video on Demand</a> (9)
 Own, Rental, x Minute</p><p style="margin-left: 5px;"><span class="red">New Option:</span> <a href="http://www.data18.com/sites/21naturals/on-demand.html/scenes">Pay per Scene</a> 40</p>
</div><div style="margin-left: 5px; margin-top: 3px; margin-bottom: 10px;" class="gen">
        <p style="font-weight: bold;" class="gen11">Performer Guide:</p>
        
<div id="listpornstars">
<select style="width: 200px; padding: 3px;">
<option selected="selected">Search Pornstars...</option>
</select>
</div>
        </div><script>              
        $(document).ready(function(){
        $("#listpornstarsdiv").one("click, mouseover", function() {
        $("#listpornstars").load("/sys/related_site3.php?s=2943");   
    });
        });
        </script></div></div></div>
<div style="clear: both;"></div><div style="height: 3px;"></div><div id="scenes"></div><div style="padding: 8px; margin-bottom: 3px;">
<p class="gen" style="font-weight: bold;">Scene Index</p>
</div><div style="background: #DADADA; padding: 10px; margin-bottom: 3px;"
 onmouseover="this.style.background='#F6F4D0'" onmouseout="this.style.background='#DADADA'">
<p><span class="gen"><b>Scene 1</b></span> &nbsp;&nbsp;00:00:12 - 00:20:36 </p>
<p class="gen12">&nbsp;Starring: <b><a href="http://www.data18.com/victoria_daniels/" class="bold">Victoria Daniels</a>, <a href="http://www.data18.com/jakub_forman/" class="bold">Jakub Forman</a>, </b></p>




<div style="float: left; margin: 8px; width: 600px; overflow: hidden;">
          
<a href="http://www.data18.com/content/1162491"><img src="http://ima1.data18.com/329/2943/162491/th5_2/03.jpg" class="yborder" alt="image1 scene Array" /></a>
&nbsp;&nbsp;
<a href="http://www.data18.com/content/1162491"><img src="http://ima1.data18.com/329/2943/162491/th5_2/06.jpg" class="yborder" alt="image2 scene Array" /></a>
&nbsp;&nbsp;
<a href="http://www.data18.com/content/1162491"><img src="http://ima1.data18.com/329/2943/162491/th5_2/08.jpg" class="yborder" alt="image2 scene Array" /></a>

</div><div style="float: left; width: 300px; height: 125px; overflow: hidden;"><div style="margin-top: 8px; background: lightblue; padding: 12px;">
<a href="https://secure.data18.com/store/scene/479012" rel="nofollow" class="big bold"
 style="color: black;">Buy this scene
 - $5.99</a>
<p>Unlimited Download & Streaming<br />Available for life on your VOD Library</p>
</div>
</div><div style="clear: both;"></div>
</div><div style="background: #f3f3f3; padding: 10px; margin-bottom: 3px;"
 onmouseover="this.style.background='#F6F4D0'" onmouseout="this.style.background='#f3f3f3'">
<p><span class="gen"><b>Scene 2</b></span> &nbsp;&nbsp;00:20:48 - 00:40:39 </p>
<p class="gen12">&nbsp;Starring: <b><a href="http://www.data18.com/dev/eveline_dellai/">Eveline Dellai</a>, <a href="http://www.data18.com/renato/" class="bold">Renato</a>, </b></p>




<div style="float: left; margin: 8px; width: 600px; overflow: hidden;">
          
<a href="http://www.data18.com/content/1162490"><img src="http://ima1.data18.com/329/2943/162490/th5_2/03.jpg" class="yborder" alt="image1 scene Array" /></a>
&nbsp;&nbsp;
<a href="http://www.data18.com/content/1162490"><img src="http://ima1.data18.com/329/2943/162490/th5_2/06.jpg" class="yborder" alt="image2 scene Array" /></a>
&nbsp;&nbsp;
<a href="http://www.data18.com/content/1162490"><img src="http://ima1.data18.com/329/2943/162490/th5_2/08.jpg" class="yborder" alt="image2 scene Array" /></a>

</div><div style="float: left; width: 300px; height: 125px; overflow: hidden;"><div style="margin-top: 8px; background: lightblue; padding: 12px;">
<a href="https://secure.data18.com/store/scene/479013" rel="nofollow" class="big bold"
 style="color: black;">Buy this scene
 - $5.99</a>
<p>Unlimited Download & Streaming<br />Available for life on your VOD Library</p>
</div>
</div><div style="clear: both;"></div>
</div><div style="background: #DADADA; padding: 10px; margin-bottom: 3px;"
 onmouseover="this.style.background='#F6F4D0'" onmouseout="this.style.background='#DADADA'">
<p><span class="gen"><b>Scene 3</b></span> &nbsp;&nbsp;00:40:53 - 01:02:10 </p>
<p class="gen12">&nbsp;Starring: <b><a href="http://www.data18.com/mona_kim/" class="bold">Mona Kim</a>, <a href="http://www.data18.com/jakub_forman/" class="bold">Jakub Forman</a>, </b></p>




<div style="float: left; margin: 8px; width: 600px; overflow: hidden;">
          
<a href="http://www.data18.com/content/1162487"><img src="http://ima1.data18.com/329/2943/162487/th5_2/03.jpg" class="yborder" alt="image1 scene Array" /></a>
&nbsp;&nbsp;
<a href="http://www.data18.com/content/1162487"><img src="http://ima1.data18.com/329/2943/162487/th5_2/06.jpg" class="yborder" alt="image2 scene Array" /></a>
&nbsp;&nbsp;
<a href="http://www.data18.com/content/1162487"><img src="http://ima1.data18.com/329/2943/162487/th5_2/08.jpg" class="yborder" alt="image2 scene Array" /></a>

</div><div style="float: left; width: 300px; height: 125px; overflow: hidden;"><div style="margin-top: 8px; background: lightblue; padding: 12px;">
<a href="https://secure.data18.com/store/scene/479014" rel="nofollow" class="big bold"
 style="color: black;">Buy this scene
 - $5.99</a>
<p>Unlimited Download & Streaming<br />Available for life on your VOD Library</p>
</div>
</div><div style="clear: both;"></div>
</div><div style="background: #f3f3f3; padding: 10px; margin-bottom: 3px;"
 onmouseover="this.style.background='#F6F4D0'" onmouseout="this.style.background='#f3f3f3'">
<p><span class="gen"><b>Scene 4</b></span> &nbsp;&nbsp;01:02:23 - 01:27:59 </p>
<p class="gen12">&nbsp;Starring: <b><a href="http://www.data18.com/tina_kay/" class="bold">Tina Kay</a>, <a href="http://www.data18.com/dev/clark/">Clark</a>, </b></p>




<div style="float: left; margin: 8px; width: 600px; overflow: hidden;">
          
<a href="http://www.data18.com/content/1162480"><img src="http://ima1.data18.com/329/2943/162480/th5_2/03.jpg" class="yborder" alt="image1 scene Array" /></a>
&nbsp;&nbsp;
<a href="http://www.data18.com/content/1162480"><img src="http://ima1.data18.com/329/2943/162480/th5_2/06.jpg" class="yborder" alt="image2 scene Array" /></a>
&nbsp;&nbsp;
<a href="http://www.data18.com/content/1162480"><img src="http://ima1.data18.com/329/2943/162480/th5_2/08.jpg" class="yborder" alt="image2 scene Array" /></a>

</div><div style="float: left; width: 300px; height: 125px; overflow: hidden;"><div style="margin-top: 8px; background: lightblue; padding: 12px;">
<a href="https://secure.data18.com/store/scene/479015" rel="nofollow" class="big bold"
 style="color: black;">Buy this scene
 - $5.99</a>
<p>Unlimited Download & Streaming<br />Available for life on your VOD Library</p>
</div>
</div><div style="clear: both;"></div>
</div><div style="height: 50px;"></div><div style="width: 900px; padding: 8px; margin-bottom: 10px;">
<p><span class="big bold">18 U.S.C.Section 2257 Compliance Statement:</span></p>
<p class="gen12">All models were at least 18 years old when they were photographed &amp; shooted.</p><p class="gen12">
Information from our official store: <a href="http://www.data18.com/store/help/cs_2257" onclick="window.open(this.href, this.target, 'width=995,height=400,top=150,left=150'); return false;"  rel="nofollow">Click Here for 18 U.S.C. 2257 information </a></p><p class="gen12">* Membership option: 21naturals and related sites are not operated by data18</p>
<p style="margin-top: -3px;">For more information about
 <span style="text-decoration: underline;">18 U.S.C.Section 2257 Compliance Statement</span>
please visit:
 <a href="http://www.data18.com/go/2943" rel="nofollow" class="bold" onclick="this.target='_blank'">
21naturals</a>
</p></div></div><div style="clear: both;"></div><div style="height: 275px; background: #f3f3f3; margin-top: 3px; padding: 10px; text-align: center;"><div style="width: 310px; height: 72px; overflow: hidden; margin-bottom: 10px;">
<div style="margin-top: -4px; margin-left: -4px;">
<a href="http://www.data18.com/sites/21naturals/"><img src="http://img.data18.com/images/pic/" alt="studio" /></a>
</div>
</div><div style="float: left; padding: 8px;">
<a href="http://www.data18.com/movies/1156685"><img src="http://img.data18.com/covers/nav/7/1156685-foot-art-1.jpg" style="width: 120px;" /></a>
</div> <div style="float: left; padding: 8px;">
<a href="http://www.data18.com/movies/1156336"><img src="http://img.data18.com/covers/nav/7/1156336-intimate-moments.jpg" style="width: 120px;" /></a>
</div> <div style="float: left; padding: 8px;">
<a href="http://www.data18.com/movies/1155248"><img src="http://img.data18.com/covers/nav/7/1155248-morning-desires.jpg" style="width: 120px;" /></a>
</div> <div style="float: left; padding: 8px;">
<a href="http://www.data18.com/movies/1154290"><img src="http://img.data18.com/covers/nav/7/1154290-one-last-time.jpg" style="width: 120px;" /></a>
</div> <div style="float: left; padding: 8px;">
<a href="http://www.data18.com/movies/1152384"><img src="http://img.data18.com/covers/nav/7/1152384-daydreaming.jpg" style="width: 120px;" /></a>
</div> <div style="float: left; padding: 8px;">
<a href="http://www.data18.com/movies/1151488"><img src="http://img.data18.com/covers/nav/7/1151488-sexy-intentions.jpg" style="width: 120px;" /></a>
</div> <div style="float: left; padding: 8px;">
<a href="http://www.data18.com/movies/1150364"><img src="http://img.data18.com/covers/nav/7/1150364-sleek-lovers.jpg" style="width: 120px;" /></a>
</div> <div style="clear: both;"></div></div><div style="width: 984; height: 234px; 
 background: #F7F7F7; margin-top: 3px; overflow: hidden;">
<a href="http://www.data18.com/go/banner/2943" rel="nofollow" onclick="this.target='_blank'">         <img src="http://img.data18.com/blocks/7627.jpg" alt="21naturals" class="noborder" /></a>

</div><div class="lfoo"><div class="block auto">
<a href="http://www.data18.com/movies/1153530#" rel="nofollow" onclick="javascript: window.scrollTo(0,0);" class="gen12 bold">Back to Top</a>
</div>
</div>
<div class="clear"></div>
<div class="dfoo1">
<p class="gen bold">About data18.com</p>
<p><a href="http://www.data18.com/sys/report.php" rel="nofollow" onclick="this.target='_blank'" class="bold">Contact Us</a> - <a href="http://www.data18.com/2257.html" rel="nofollow" onclick="this.target='_blank'" class="bold">18 U.S.C. 2257</a></p>
<p>Do you like data18? <a href="http://www.data18.com/share.html" rel="nofollow" class="bold" onclick="this.target='_blank'">Share us!</a></p>
<p>Follow us: <a href="http://www.data18.com/rss.html" class="red" rel="nofollow">RSS Feeds</a> - <a href="http://www.twitter.com/data18" class="blue" rel="nofollow" onclick="this.target='_blank'">Twitter</a> @data18</p>
<p>We support the use of filtering software which prevents minors from accessing inappropriate material: <a href="http://cyberpatrol.com" rel="nofollow" onclick="this.target='_blank'">CyberPatrol</a> | <a href="http://www.pandasecurity.com/about/social-responsibility/children-internet/" rel="nofollow" onclick="this.target='_blank'">Panda</a> | <a href="http://www.netnanny.com" rel="nofollow" onclick="this.target='_blank'">Net Nanny</a></p>
</div>
<div class="dfoo2">
<p><a href="http://www.data18.com/sitemap.html" class="gen bold">Sitemap</a></p>
<p>- <a href="http://www.data18.com/pornstars/">Pornstars</a></p>
<p>- <a href="http://www.data18.com/movies/">Movies</a> </p>
<p>- <a href="http://www.data18.com/studios/">Studios</a></p>
<p>- <a href="http://www.data18.com/content/">Content</a> </p>
<p>- <a href="http://www.data18.com/sites/">Sites &amp; Networks</a></p>
<p>- <a href="http://www.data18.com/awards/">Porn Awards</a></p>
</div>
<div class="dfoo3">
<p class="gen bold">About our Store:</p>
<p>Buy <a href="http://www.data18.com/movies/dvd.html" class="bold">DVDs</a>, <a href="http://www.data18.com/movies/blu-ray.html" class="bold">Blu-Ray</a>, <a href="http://www.data18.com/movies/vod.html" class="bold">Video on Demand</a> and <a href="http://www.data18.com/sex-toys/" class="bold">Sex Toys</a>.</p>
<p>The Store is provided by <a href="http://www.adultempirecash.com" rel="nofollow" onclick="this.target='_blank'">Empire Stores</a>:<br /><a href="http://www.data18.com/store/help/cs_2257" onclick="window.open(this.href, this.target, 'width=980,height=400,top=150,left=150'); return false;"  rel="nofollow">18 U.S.C. 2257</a> - <a href="http://www.data18.com/store/help/terms_of_use" onclick="window.open(this.href, this.target, 'width=980,height=600,top=150,left=150'); return false;"  rel="nofollow">Terms of Use</a> - <a href="http://www.data18.com/store/help/privacy_policy" onclick="window.open(this.href, this.target, 'width=980,height=600,top=150,left=150'); return false;"  rel="nofollow">Privacy Policy</a></p>
<p> Visit our store in "Full Mode", <a href="http://store.data18.com" rel="nofollow" onclick="this.target='_blank'">Click Here</a></p>
<p><span class="bold">Customer Service:</span> <a href="http://www.data18.com/store/help" rel="nofollow">Help Center</a> <a href="http://store.data18.com/account/inquiry" rel="nofollow" onclick="this.target='_blank'">Ask a Question</a> <a href="http://www.data18.com/store/help" rel="nofollow">Chat live</a></p>
<p><a href="http://www.data18.com/store/help/discreet_service" rel="nofollow">Discreet Service</a> - <a href="http://www.data18.com/store/help/shipping" rel="nofollow">Shipping Methods and Rates</a> - <a href="http://www.data18.com/store/help/return_policy" rel="nofollow">Return Policy</a>
</p>           
</div><div class="dsecure genmed">
<div class="bso spr-secure"></div>
<p>Transaction process is safe and customers' information is secure.</p>
<p>data18 encrypts confidential information with the Secure Sockets Layer (SSL)</p>
</div>
<div class="clear"></div>
</div>
</div>
<script type="text/javascript">
$(document).ready(function() {
$("a.grouped_elements").fancybox();
$("#searchform").focus();
});      


</script><div id="finalbody"></div>






</body>
</html>

    '''
    # html = requests.get('http://www.data18.com/movies/156760',headers={
    #         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}).text
    # print(html.text)
    soup = BeautifulSoup(html1, "lxml")
    div_main = soup.text

    info_txt = soup.select_one('#centered > div.p8 > div:nth-of-type(7) > div').text
    # infos = re.search(r'<h1.*>(?P<title>.*)</h1>.*Release date: (?P<date>.*\d{4}).*'
    #                   r'((Studio)|(Site)):</b> (?P<writer>.*)\s*\|\s*'
    #                   r'<b>Director:</b>\s*(?P<director>.*?)</p>.*'
    #                   r'<b>Categories:</b>(?P<gener>.*?)'
    #                   r'<b>Description:</b>.*?>(?P<des>.*?)</p></div>'
    #                   ,html3,re.S)

    # if not infos:
    #     infos = re.search(r'<h1.*>(?P<title>.*)</h1>.*Release date: (?P<date>.*\d{4}).*'
    #                       r'((Studio)|(Site)):</b> (?P<writer>.*)\s*\|\s*'
    #                       r'<b>Director:</b>\s*(?P<director>.*?)</p>.*'
    #                      r'(?P<gener>.*)'
    #                       r'<b>Description:</b>.*?>(?P<des>.*?)</p></div>'
    #                       , html2, re.S)


    # print(info_txt)


    infos = re.search(r'Release date:(?P<date>.*?)\s*?(?:(Studio)|(Site)):(?P<writer>.*?)\s*?\|\s*?Director:\s*?(?P<director>.*?)\s*?'
                      r'(?:Movie Length.*?)?'
                      # r'(?P<gener>Categories:.*?)?'
                      r'Description:\s*?(?P<des>.*)',info_txt,re.S)


    # print('title:',infos.group('title').strip())
    print('date:',infos.group('date').strip())
    print('writer:',infos.group('writer').strip())
    print('director:',infos.group('director').strip())
    # print('gener:',infos.group('gener'))
    print('des:',infos.group('des').strip())
    #
    # actor_div = soup.select('#centered > div.p8 > div:nth-of-type(10) > div > div > div')
    # actors = [actor.text.strip() for actor in actor_div]
    # actor_more = soup.select('#centered > div.p8 > div:nth-of-type(10) > div > p:nth-of-type(2) > a')
    # if actor_more:
    #     actors.extend([actor.text.strip() for actor in actor_more])
    #
    # print(actors)
    #
    # generlst = re.findall('(.+?\s)',infos.group('gener')+' ')
    # #
    # print(generlst)



    # actors_txt = soup.select_one('#centered > div.p8 > div:nth-of-type(10) > div').text
    # # print(actors_txt.split('\n',','))
    # # print([each for each in actors_txt])
    # actors = re.findall(r'\w+\n*?',actors_txt,re.S)
    # print(actors)

    # actor = re.search(r'',actors_txt,re.S)

    # print(infos.group('writer'))

    # info = re.search('Release date:.*?</p></div>',html,re.S)
    # actors = re.search('<div class="contenedor"(.*?)</p>.*?</div>.*?</div>.*?<div',html,re.S)


    # print(BeautifulSoup('<div>'+info.group(0), "lxml").text,BeautifulSoup(actors.group(1), "lxml").text)
    # w_d = div_main.select_one('div.gen12 > p:nth-of-type(2)')
    # writers = re.search( r'<b>(?:Site|Studio):</b> (.*?) \| <b>Director:</b>(.*?)</p>',str(w_d),re.S)
    # if writers:
    #     if writers.group(1):
    #         writer= writers.group(1)
    #         writer_a = re.search(r'<a.*?>(.*)</a>',writer)
    #         if writer_a:
    #             writer = writer_a.group(1)
    #
    #     if writers.group(2):
    #         director = writers.group(2)
    #         director_a = re.search(r'<a.*?>(.*)</a>', director)
    #         if director_a:
    #             director = director_a.group(1)



    # writers = re.search(r'<b>(?:Site)|(?:Studio):</b>(.*?)</a>', w_d).group(1)

    # print(writer,director)
    # with open('/Users/syaofox/Downloads/7269a4c5jw1en93mk6k6fj21kw23ualz_cover.jpg','rb') as f:
    #     poster = f.read()
    # with open('/Users/syaofox/Downloads/w.jpg','rb') as f:
    #     backdrop = f.read()
    #
    #
    # merge_image(poster,backdrop)

    # # opens an image:
    # im = Image.open("/Users/syaofox/Downloads/shermie98.jpg")
    # # creates a new empty image, RGB mode, and size 400 by 400.
    # new_im = Image.new('RGB', (400, 400))
    #
    # # Here I resize my opened image, so it is no bigger than 100,100
    # im.thumbnail((100, 100))
    # # Iterate through a 4 by 4 grid with 100 spacing, to place my image
    # for i in range(0, 500, 100):
    #     for j in range(0, 500, 100):
    #         # I change brightness of the images, just to emphasise they are unique copies.
    #         im = Image.eval(im, lambda x: x + (i + j) / 30)
    #         # paste the image at location i,j:
    #         new_im.paste(im, (i, j))
    #
    # new_im.show()






    # image_merge(images=['/Users/syaofox/Downloads/shermie98.jpg', '/Users/syaofox/Downloads/7269a4c5jw1en93mk6k6fj21kw23ualz_cover.jpg', 'xxxx.jpg'])
