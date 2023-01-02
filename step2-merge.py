import os
import json
from matplotlib.font_manager import json_load
import requests
import time

PATH = os.path.abspath(os.path.dirname(__file__))
main_path = os.path.join(PATH, 'Sina')

save_dict = 'total_data.json'

""" STEP-2 """


# headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}

headers = \
    {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
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


def get_comment_show_num(article):
    timestamp = int(time.time() * 1000)

    commentid = article['commentid']
    docid = article['docid']

    channel = commentid.split(':')[0]
    docid =docid.replace(":", "-")

    payload = {
	    'version': '1',
        'format': 'json',
        'channel': channel,
        'newsid': docid,
        'group': '0',
        'compress': '0',
        'ie': 'utf-8',
        'oe': 'utf-8',
        'page': '1',
        'page_size': '3',
        't_size': '3',
        'h_size': '3',
        'thread': '1',
        'uid': 'unlogin_user',
        'callback': f'jsonp_{str(timestamp)}',
        '_': str(timestamp),
	 }
    response = requests.get("https://comment.sina.com.cn/page/info", params=payload, headers=headers)
    ret = json.loads(response.text[20:-1])
    try:
        comment_show_num = int(ret['result']['count']['show'])
        return comment_show_num
    except:
        print(ret)
        comment_show_num = 0
        return comment_show_num


def delete_all_total_data():
    """ 删除 total_data.json文件"""

    main_path = os.path.join(PATH, 'Sina')
    for new_type in os.listdir(main_path):
        new_type = os.path.join(main_path, new_type)
        total_data_path = os.path.join(new_type, 'total_data.json')

        if os.path.exists(total_data_path):
            os.remove(total_data_path)
            print(f'{total_data_path} is remove!')
        else:
            print(f'{total_data_path} is not exist!')


def remove_irrelevant_file(new_type_dir):
    irrelevant_filename = ['total_data.json', 'images', 'data_total_all.json', 'temp.json', 'data_total_all_userinfo.json']
    for item in new_type_dir:
        if str(item) in irrelevant_filename:
            new_type_dir.remove(item)

    # 非常奇怪，data_total_all_userinfo.json 不能与irrelevant_filename相同进行匹配检索
    try:
        new_type_dir.remove('data_total_all_userinfo.json')
    except:
        print('data_total_all_userinfo.json  is not exist!')


    return new_type_dir


def main():
    """ comment_show = 0 时直接赋值为0即可， 依据，每日采集的数据有重复且会覆盖之前 comment_show 的值 """
    for new_type in os.listdir(main_path):
        new_type = os.path.join(main_path, new_type)

        new_type_dir = os.listdir(new_type)
        total_data_path = os.path.join(new_type, save_dict)

        if not os.path.exists(total_data_path):
            total_data_dict = {}
        else:
            with open(total_data_path, 'r', encoding='utf-8') as f:
                total_data_dict = json.load(f)

        new_type_dir =remove_irrelevant_file(new_type_dir)

        print(new_type)

        for date in new_type_dir:
            path = os.path.join(new_type, date)
            filename = os.listdir(path)[0]
            file_path = os.path.join(new_type, date, filename)

            with open(file_path, 'r', encoding='utf-8') as load_f:
                load_dict = json.load(load_f)
                for i in range(len(load_dict)):

                    # 将 title作为字典的key
                    Title = load_dict[i]['title']

                    # 若每日采集的数据不存在 comment_show 字段， 则添加该字段
                    if not 'comment_show' in load_dict[i].keys():
                        load_dict[i]['comment_show'] = 0

                    # 若新闻不在total_data_dict中，则该新闻被新增加
                    if Title  not in total_data_dict:
                        print('update news ', Title)
                        total_data_dict.update({Title: load_dict[i]})

                    else:
                        # 若该新闻存在，但total_data_dict 中 comment_show 的值 小于 load_dict 中 comment_show 的值，则更新
                        if int(total_data_dict[Title]['comment_show']) < int(load_dict[i]['comment_show']):
                            print(f"ori total_data_dict comment_show {total_data_dict[Title]['comment_show']} update to {load_dict[i]['comment_show']}")
                            total_data_dict[Title]['comment_show'] = int(load_dict[i]['comment_show'])

        data_save(total_data_dict, new_type + '/total_data.json')


if __name__ == '__main__':
    main()


