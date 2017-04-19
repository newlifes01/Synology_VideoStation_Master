#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import string
from datetime import datetime
from time import mktime, strptime
from urllib.parse import urlencode, quote

import os
import re
from PIL import Image, ImageChops
from PyQt5.QtCore import QFile
from collections import OrderedDict
# 日志登记
from io import BytesIO

logging.basicConfig(level=logging.INFO)
# 下载最大重试次数
RETRYMAX = 5
# 下载超时时间
DOWN_TIME_OUT = 15
# 爬虫下载间隔
SPIDER_DOWNLOAD_SLEEP_TIME = 0.1

# 项目根目录
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
# 临时目录
CACHE_PATH = os.path.join(PROJECT_PATH, '.cache')
# 缓存文件路径
DSM_CACHE_PATH = os.path.join(PROJECT_PATH, 'http_cache.sqlite')

# 缓存保留时间 秒
CACHE_KEEP_TIME = 3600 * 24
# 图片是否永久缓存
IMG_CACHE_KEEP_INFINITE = True
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

SAMPLES_SAVE_PACH = '/Users/syaofox/Downloads/dsm_master_samples'

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
            'xy':()

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
        return datetime.strptime(date_str, '%m/%d/%Y').strftime('%Y-%m-%d')
    except Exception:
        pass


    try:
        return datetime.strptime(date_str, '%Y/%m/%d').strftime('%Y-%m-%d')
    except Exception:
        pass
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


def IsValidImage(indata):
    bValid = True
    buf = indata
    if isinstance(indata, bytes):
        buf = BytesIO(indata)

    try:
        Image.open(buf).verify()
    except:
        bValid = False

    return bValid


def merge_image(poster, bakdrop):
    try:
        out = BytesIO()

        stream = BytesIO(poster)
        im_poster = Image.open(stream)

        stream = BytesIO(bakdrop)
        im_bakdrop = Image.open(stream)

        im_bakdrop = im_bakdrop.resize(im_poster.size, Image.ANTIALIAS)

        new_im = Image.new('RGB', (im_poster.size[0] * 2, im_poster.size[1]))

        new_im.paste(im_bakdrop, (0, 0))
        new_im.paste(im_poster, (im_poster.size[0], 0))

        new_im.save(out, format='JPEG')
        return out.getvalue()
    except Exception:
        pass


def format_filename(s):

    # remove_punctuation_map = dict((ord(char), None) for char in '\/*?:"<>|')
    # return s.translate(remove_punctuation_map)

    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace(' ', '_')  # I don't like spaces in filenames.
    return filename

if __name__ == '__main__':
    str = quote('金髪天国',encoding='euc-jp')
    print(str)