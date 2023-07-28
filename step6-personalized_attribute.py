import json
import os
import sys
from tqdm import tqdm
from collections import Counter


"""
将每个类别中的数据那评论字段是否完整进行过滤。
然后把每个类合格的数据合并在一起构成一个完整的数据集

"""


def data_save(data, path):
    json.dump(data, open(path , 'w', encoding='utf-8'), indent=4, ensure_ascii=False)


def data_read(path):
    with open(path, 'r', encoding='utf-8') as load_f:
        load_dict = json.load(load_f)
    return load_dict



def filter_comment(data_total_all_userinfo_dict, category):
    "过滤评论，要求属性全字段的评论为过滤目标"
    new_data_total_all_userinfo = {}

    category_num = 0

    with tqdm(data_total_all_userinfo_dict.items(), desc='filter the comment ' + category, file=sys.stdout, disable=False) as data_total_all_userinfo_dict_iterator:
        for key, value in data_total_all_userinfo_dict_iterator:

            # 判断文章是否有评论
            comments_num = len(value['comments']['newest_comments'])
            if comments_num > 0:

                comments = value['comments']['newest_comments']
                for comment in comments:

                    content = comment['content']
                    if len(content) == 0:
                        print("content == None")

                    userinfo = comment['userinfo']

                    try:
                        birthday = userinfo['birthday'].strip()
                    except:
                        birthday = ''
                        userinfo.update({'birthday': birthday})

                    try:
                        description = userinfo['description'].strip()
                    except:
                        description = '暂无简介'
                        userinfo.update({'description': description})

                    try:
                        gender = userinfo['gender'].strip()
                    except:
                        gender = ''
                        userinfo.update({'gender': gender})

                    try:
                        location = userinfo['location'].strip()
                    except:
                        location = '其他'
                        userinfo.update({'location': location})


                    if birthday!= '' and gender != '' and location != '' and description != '' :
                    # if description != '':
                        comment = {
                                    comment['uid']:{
                                    "content": comment['content'],
                                    "userinfo":{
                                        "nick": comment['nick'],
                                        "birthday": userinfo['birthday'],
                                        "description":  userinfo['description'],
                                        "gender":  userinfo['gender'],
                                        "location":  userinfo['location'],
                                    },
                                    "sentiment": None,
                                }
                            }

                        saving_format = {
                            "title": value['title'],
                            "label": category,
                            "keywords": value['keywords'],
                            "images": value['images'],
                            "content": value['article'],
                            "comments": [comment]
                        }

                        if key in new_data_total_all_userinfo:
                            new_data_total_all_userinfo[key]['comments'].append(comment)
                        else:
                            new_data_total_all_userinfo.update({key: saving_format})

                        category_num += 1


        print(category_num)

        return category_num, new_data_total_all_userinfo


def main(path):
    saving_path = os.path.join(path, 'Sina_filter_attribute_25k.json')
    categories = ['ent', 'guoji', 'guonei', 'military', 'money', 'social', 'sport', 'stock', 'tech', 'US_stock']

    total_new_data_total_all_userinfo = {}
    total_num = 0

    for item in categories:
        path_cat = os.path.join(path, item, 'data_total_all_userinfo.json')
        data_total_all_userinfo_dict = data_read(path_cat)
        category_num, new_data_total_all_userinfo = filter_comment(data_total_all_userinfo_dict, item)

        total_new_data_total_all_userinfo.update(new_data_total_all_userinfo)
        total_num += category_num

    data_save(total_new_data_total_all_userinfo, saving_path)
    print(total_num)

if __name__ == '__main__':
    path = './Sina'
    main(path)
