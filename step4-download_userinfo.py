import os
import json
from urllib import response
import requests
from bs4 import BeautifulSoup
from sympy import im
import sys
from tqdm import tqdm
import time


PATH = os.path.abspath(os.path.dirname(__file__))

# cookie 是请求userinfo必须的字段
headers = \
    {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': 'SINAGLOBAL=5679184650293.409.1639449098290; _ga_NNQRFSG6W5=GS1.1.1647865209.1.0.1647865209.0; _ga=GA1.1.1902677423.1647865213; UOR=www.google.com,www.weibo.com,www.baidu.com; ULV=1654589721983:5:1:1:939327158190.5593.1654589721976:1652176533193; XSRF-TOKEN=hbAaV19hNemPCmjLgHxtYiUa; WBPSESS=BP4XMQoD7Z31Vf3tBPaOoRTg-NmL-iCAggza2BAl_Ig4d_2HxxVBoG5ljKHwzvPxQptt1RUcXnnAvI_EgCqsEdRDFqfM6OLwHgZRrItyEI-0ZaS0ylbtITcIxtRWEbUnT7sc65mAUgKvbnw4QpuvynSqaEUCM1Lm5sM2AE23-EM=; SUB=_2AkMViinmf8NxqwFRmPwcxG_haYl3ywnEieKj1tg9JRMxHRl-yT9kqncvtRB6PgoHCU59J996UzgvNXwrc-vcdkm55lXF; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WFciphvUqr2zQ2UMyg4WSjs',
        'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "Windows",
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    }


def data_save(data, path):
    json.dump(data, open(path , 'w', encoding='utf-8'), indent=4, ensure_ascii=False)


def data_read(path):
    with open(path, 'r', encoding='utf-8') as load_f:
        load_dict = json.load(load_f)
    return load_dict


def request_data(url):
    try:
        response  = requests.get(url, headers=headers)
        response.close()
    except:
        print('HTTPSConnection Timeout')
        response = {'status_code': 404, 'encoding': 'utf-8'}
    return response


def request_data_with_param(url, params):
    response  = requests.get(url, params=params, headers=headers)
    response.close()
    return response


def userinfo_download(uuid):
    url = f"https://weibo.com/ajax/profile/detail?uid={str(uuid)}"

    response = request_data(url)

    try:
        response.encoding = 'utf-8'

        # 当响应码非200时，直接跳过
        status_code = response.status_code
        if status_code == 200:
            response = json.loads(response.text)
            data = response['data']
        else:
            data = {}
    except:
        print(f'{url} get userinfo failed!')
        data = {}

    return data


def download(data_path, new_type, data_total_all_userinfo_path):
    data_dict = data_read(data_path)

    with tqdm(data_dict.items(), desc=new_type + ' Update Download', file=sys.stdout, disable=False) as data_dict_iterator:
        for _, value in data_dict_iterator:

            # 判断 最新评论字段中 是否有评论内容
            if  value['comments']['newest_comments'] != []:

                # 获取评论的数量
                comments_len = len(value['comments']['newest_comments'])

                for index in range(comments_len):

                    # 1.判断 userinfo 字段是否存在
                    comment = value['comments']['newest_comments'][index]
                    if not 'userinfo' in comment.keys():
                        uuid = value['comments']['newest_comments'][index]['uid']
                        userinfo = userinfo_download(uuid)

                        # 用户信息添加到 userinfo 字段中
                        comment['userinfo'] = userinfo

                    # 2.若 userinfo 字段为空则需要重新求更更新字典
                    elif comment['userinfo'] == {}:
                        uuid = value['comments']['newest_comments'][index]['uid']
                        userinfo = userinfo_download(uuid)

                        # 更新原有空字典的内容
                        comment['userinfo'] = userinfo


        # 保存数据
        data_save(data_dict, data_total_all_userinfo_path)



def main():
    main_path = os.path.join(PATH, 'Sina')

    for new_type in os.listdir(main_path):
        # if new_type == 'money':

        new_type = os.path.join(main_path, new_type)

        data_total_all_path =  os.path.join(new_type, 'data_total_all.json')
        data_total_all_userinfo_path =  os.path.join(new_type, 'data_total_all_userinfo.json')

        if  os.path.exists(data_total_all_path):

            if not os.path.exists(data_total_all_userinfo_path):
                # 若 data_total_all_userinfo.json 文件不存在时，读取数据源来自 data_total_all_path (data_total_all.json)
                download(data_total_all_path, new_type, data_total_all_userinfo_path)
            else:
                # 若 data_total_all_userinfo.json 存在，读取数据源来自 data_total_all_userinfo_path (data_total_all_userinfo.json)
                download(data_total_all_userinfo_path, new_type, data_total_all_userinfo_path)

        else:
            print(f'{data_total_all_path} file is not exist!')

        # break



if __name__ == '__main__':
    main()


