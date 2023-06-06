import json
from multiprocessing.sharedctypes import Value
import os


PATH = os.path.abspath(os.path.dirname(__file__))

"""
清洗流程：
    step1：
        去掉newest_comments_len为0的数据

    step2：
        在comment中去除人设为空数据

     由于内存的限制，目前该代码还不能执行，需要到LAB上执行
"""

def data_save(data, path):
    json.dump(data, open(path , 'w', encoding='utf-8'), indent=4, ensure_ascii=False)


def data_read(path):
    with open(path, 'r', encoding='utf-8') as load_f:
        load_dict = json.load(load_f)
    return load_dict


def num_statistics(data_total_all_userinfo, new_type):
    dict_num = len(data_total_all_userinfo)
    print(new_type.split('/')[-1], dict_num)

    return dict_num


def filter_newest_comments(data_total_all_userinfo):
    filter_comment_data = {}

    for key, value in data_total_all_userinfo.items():
        newest_comments_len = len(value['comments']['newest_comments'])

        if newest_comments_len != 0:
            filter_comment_data.update({key: value})

    return filter_comment_data


def filter_userinfo(filter_comment_data):
    filter_userinfo_data = {}

    for key, value in filter_comment_data.items():
        newest_comments = value['comments']['newest_comments']

        for comment in newest_comments:
            if comment['userinfo'] != {}:
                filter_userinfo_data.update({key: value})

    return filter_userinfo_data


def add_label(filter_userinfo_data, new_type):
    label = new_type.split('/')[-1]

    for key, value in filter_userinfo_data.items():
        value.update({'label': label})

    return filter_userinfo_data


def data_merage(total_label_data, SinaDataset, ReatNum):
    for key, value in total_label_data.items():
        if key in SinaDataset:
            ReatNum += 1
            print(key)

    SinaDataset.update(total_label_data)

    return SinaDataset, ReatNum


def count_Sina():
    SinaData = data_read('./Sina_ori.json')
    print(len(SinaData))


def main():
    main_path = os.path.join(PATH, 'Sina')

    SinaDataset = {}

    total_ori_num = 0
    total_comment_num = 0
    total_userinfo_num = 0
    ReatNum = 0


    for new_type in os.listdir(main_path):

        new_type = os.path.join(main_path, new_type)
        data_total_all_userinfo_path =  os.path.join(new_type, 'data_total_all_userinfo.json')

        data_total_all_userinfo = data_read(data_total_all_userinfo_path)

        # 统计 原始数据集数量
        ori_num = num_statistics(data_total_all_userinfo, new_type)
        total_ori_num += ori_num

        # step 1 去掉newest_comments_len为0的数据
        filter_comment_data = filter_newest_comments(data_total_all_userinfo)

        # 统计 过滤评论
        comment_num = num_statistics(filter_comment_data, new_type)
        total_comment_num += comment_num


        # step 2 在comment中去除人设为空数据
        filter_userinfo_data = filter_userinfo(filter_comment_data)

        # 统计 过滤userinfo
        userinfo_num = num_statistics(filter_userinfo_data, new_type)
        total_userinfo_num += userinfo_num

        # 增加label字段
        total_label_data = add_label(filter_userinfo_data, new_type)

        # 数据合并
        # SinaDataset.update(total_label_data)
        SinaDataset, ReatNum = data_merage(total_label_data, SinaDataset, ReatNum)

    print('total_ori_num', total_ori_num)
    print('total_comment_num', total_comment_num)
    print('total_userinfo_num', total_userinfo_num)
    data_save(SinaDataset, './Sina_ori.json')
    print('Repeat Number', ReatNum)


if __name__ == '__main__':
    main()
    count_Sina()
