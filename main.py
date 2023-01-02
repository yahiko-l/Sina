import code
from importlib.resources import path
from lib2to3.pgen2 import pgen
from urllib import response
from numpy import roll
import requests
import json
import os
import time
import datetime
from lxml import etree
import re


"""
Step 1, 新浪新闻爬虫, 每天固定执行时间 13:30
"""

headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/\
            537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}


today=str(datetime.datetime.now())[5:7]+str(datetime.datetime.now())[8:10]
print(today)


def request_param(news_type, page_num):
    request_data = {
                    'pageid': '153',
                    'lid': str(news_type),
                    'k': '',
                    'num': '50',
                    'page': str(page_num),
                    }

    return request_data


def request_data(url, params):
    """ 请求URL数据 """
    response  = requests.get(url, params=params, headers=headers)
    response.close
    return response


def parse_data(response):
    request_url = response.url
    response = response.text
    try:
        response = json.loads(response)
        msg = response['result']['status']['msg']
        if msg == 'succ':
            data = response['result']['data']
        else:
            data = []
            print('msg is ', msg)
    except:
        print('页面不存在', request_url)
        data = []

    return data


def format_time():
    """
    生成时间格式-作为文件名称
    """

    t = time.localtime()
    # Time = time.strftime("%Y-%m-%d-%H:%M:%S", t)
    Time = time.strftime("%Y-%m-%d-%H", t)
    return Time


def make_dir(dir_name):
    """
    根据目录以及子目录创建文件夹
    如 Sina/ent/2022-05-29-22(时间区别)
     """
    root_path = os.path.abspath(os.path.dirname(__file__))

    root_path = root_path + '/Sina/'

    if not os.path.exists(root_path):
        os.mkdir(root_path)

    path = root_path + dir_name
    if not os.path.exists(path):
        os.mkdir(path)

    path = root_path + dir_name + '/' + format_time()
    if not os.path.exists(path):
        os.mkdir(path)

    return path


def save_data_callback(path, data):
    """
    保存 callback 中数据组字典
    """
    path = path + '/' + today + '.json'
    json.dump(data, open(path , 'w', encoding='utf-8'), indent=4, ensure_ascii=False)


def parse_external_data(response):
    request_url = response.url
    response = response.text
    # response = response[42:-1]
    try:
        code = 200
        response = json.loads(response)
        data = response['data']
        if data == None:
            data = []

    except:
        print('页面不存在', request_url)
        code = 404
        data = []

    return data


def external_param(news_type, page, mod, action):
    external_url = 'https://interface.sina.cn/pc_api/public_news_data.d.json'

    # 科技页面
    if news_type == 2515:
        param = {
                # 'callback': 'jQuery1112032385657514527133_1653915406629',
                'mod': mod,
                'cids': '40810,40811,40812',
                'editLevel': '0,1,2,3',
                'cre': 'tianyi',
                'merge': '3',
                'statics': '1',
                'length': '15',
                'up': str(page),
                'down': '0',
                'tm': '1653915407',
                'action': str(action),
                'top_id': 'tXPlV,tZ6G7,tYMZB,tYMqV,tZTOD,tZXpX,tZa6B,tYbS2,t1lEI,,',
                'offset': '0',
                'ad': '{"rotate_count":100,"platform":"pc","channel":"tianyi_pctech","page_url":"https://tech.sina.com.cn/","timestamp":1653915406937}',
                'pdps': '',
                'type': 'std_news,std_slide,std_video',
                'pageSize': '20',
                'cTime': '1653656215',
                '_': '1653915406632',
            }
    # 体育页面
    elif news_type == 2512:
        param = {
            # 'callback': 'jQuery111306131549554659566_1653914148362',
            'cre': 'tianyi',
            'mod': mod,
            'merge': '3',
            'statics': '1',
            'tm': '1653915133',
            'offset': '0',
            'action': str(action),
            'up': str(page),
            'down': '0',
            'cids': '57307',
            'pdps':'',
            'top_id':'',
            'smartFlow':'',
            'editLevel': '0, 1, 2, 3, 4',
            'pageSize': '12',
            'type': 'sports_news, sports_slide, sports_video, common_video_sports',
            'ad': '{"rotate_count":100,"platform":"pc","channel":"tianyi_pcspt","page_url":"http://sports.sina.com.cn/","timestamp":1653914148375 }',
            '_': '1653914148400',
        }
    # 娱乐页面
    elif news_type == 2513:
        param = {
            # 'callback': 'jQuery111206726843881580926_1653904316997',
            'cre': 'tianyi',
            'mod': mod,
            'merge': '3',
            'statics': '1',
            'length': '15',
            'up': str(page),
            'down': '0',
            'tm': '1653904317',
            'action': str(action),
            'top_id': 'ta1kJ,taL6K,ta1kJ,tYwW3,ta0jp,tZmwH,tZWaW,tZPcV,tYeiJ,tV8Zl,tV8Zl,tVNOD,tVsgs,tV5Qf',
            'offset': '0',
            'cids': '34765',
            'pdps': '',
            'smartFlow': 'ent_web_index_v2017_tianyistar_top',
            'type': 'std_news,std_slide,std_video',
            'editLevel': '0,1,2,3',
            'pageSize': '15',
            'cTime': '1653213120',
            '_': '1653904317009',
        }

    response = request_data(external_url, param)
    data = parse_external_data(response)

    return data


def external_callback(mods, news_type):
    general_data = []
    for mod in mods:
        page = 0
        sub_type_data = []
        while True:
            print(f'current {mod} page is {page}')
            if page == 0:
                action = 0
            else:
                action = 1

            data = external_param(news_type, page, mod, action)

            # 返回页面为空，就停止页面访问
            if data == []:
                print(f'{mod} max page is {page}')
                break

            sub_type_data.extend(data)
            page += 1

        general_data.extend(sub_type_data)
    return general_data


def main():
    roll_news_url = 'https://feed.mix.sina.com.cn/api/roll/get?'

    type_dict_CN = {
        "2510": "国内",
        "2511": "国际",
        "2669": "社会",
        "2512": "体育",
        "2513": "娱乐",
        "2514": "军事",
        "2515": "科技",
        "2516": "财经",
        "2517": "股市",
        "2518": "美股",
    }

    type_dict_EN = {
        "2510": "guonei",
        "2511": "guoji",
        "2669": "social",
        "2512": "sport",
        "2513": "ent",
        "2514": "military",
        "2515": "tech",
        "2516": "money",
        "2517": "stock",
        "2518": "US_stock",
    }

    mods_tech = ['nt_home_tech_news', 'nt_home_tech_chuangshiji', 'nt_home_tech_mobil', 'nt_home_tech_digi',
                'nt_home_tech_discovery', 'nt_home_tech_apple', 'nt_home_tech_chuangye', 'nt_home_tech_zhongce']

    mods_sport = ['nt_home_sports_nba', 'nt_home_sports_global', 'nt_home_sports_china',
                'nt_home_sports_cba', 'nt_home_sports_others', ]

    mods_ent = ['nt_home_ent_star', 'nt_home_ent_pic', 'nt_home_ent_movie',
            'nt_home_ent_tv', 'nt_home_ent_zy', 'nt_home_ent_yy', 'nt_home_ent_kpop']

    MaxPageNum = 50
    news_types = [2510, 2511, 2669, 2512, 2513, 2514, 2515, 2516, 2517, 2518]

    for news_type in news_types:
        general_data = []
        # 创建目录
        dir_name = type_dict_EN[str(news_type)]
        path = make_dir(dir_name)
        for page_num in range(1, MaxPageNum + 1):
            print(type_dict_CN[str(news_type)], page_num)

            params = request_param(news_type, page_num)
            response = request_data(roll_news_url, params)
            data = parse_data(response)
            general_data.extend(data)

        # 请求额外数据页面
        # 娱乐页面
        if news_type == 2513:
            external_data = external_callback(mods_ent, news_type)
            general_data.extend(external_data)
        # 体育页面
        elif news_type == 2512:
            external_data = external_callback(mods_sport, news_type)
            general_data.extend(external_data)
        # 科技页面
        elif news_type == 2515:
            external_data = external_callback(mods_tech, news_type)
            general_data.extend(external_data)

        # 保存在数据
        save_data_callback(path, general_data)
        print(f"<---------[ {type_dict_CN[str(news_type)]} ]数据保存完毕！-------->")


if __name__ == '__main__':
    main()


