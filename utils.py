#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from time import mktime, strptime

import os
import re
from PyQt5.QtCore import QFile

# 日志登记
logging.basicConfig(level=logging.DEBUG)
# 下载最大重试次数
RETRYMAX = 5
# 项目根目录
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
# 临时目录
CACHE_PATH = os.path.join(PROJECT_PATH, '.cache')
# 缓存文件路径
DSM_CACHE_PATH = os.path.join(PROJECT_PATH, 'http_cache.sqlite')
# 爬虫下载间隔
SPIDER_DOWNLOAD_SLEEP_TIME = 0.1
# 爬虫缓存保留时间 秒
SPIDER_CACHE_KEEP_TIME = 3600
# 缓存保留时间 秒
CACHE_KEEP_TIME = 60
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
    list_str = re.sub(r'([,，\s]+)', ',', list_str.strip())
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
        res = re.search(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', date_str)
        if res:
            return '{}-{}-{}'.format(res.group(1), res.group(2).zfill(2), res.group(3).zfill(2))

        res = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', date_str)
        if res:
            return '{}-{}-{}'.format(res.group(3), res.group(1).zfill(2), res.group(2).zfill(2))

        res = re.match(r'(\d{4})[/-](\d{1,2})', date_str)
        if res:
            return '{}-{}-{}'.format(res.group(1), res.group(2).zfill(2), '01')
        return ''
    except:
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


if __name__ == '__main__':
    pass
    print(format_time_stamp('2017-03-24 14:50:46.602983'))
    print(format_time_stamp('Mon, 13 Mar 2017 00:16:37 GMT'))



    # a = "Sat Mar 28 22:24:24 2016"
    # print(mktime(time.strptime(a, "%a %b %d %H:%M:%S %Y")))
    #
    # print(re.sub(r'([,，\s]+)', ',', 'aaa,bbb ccc   ddd，eee'))
    #
    # import sqlite3
    #
    # conn = sqlite3.connect('x.db')
    # cursor = conn.cursor()
    # cursor.execute('create table test (id varchar(20) primary key, name image)')
    # cursor.execute('insert into test (id, name) values (\'1\', \'xxx\')')
    # print(cursor.rowcount)
    # cursor.close()
    # conn.commit()
    # conn.close()
