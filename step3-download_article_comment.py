import os
import json
import requests
from bs4 import BeautifulSoup
from sympy import im
import sys
from tqdm import tqdm
import time


PATH = os.path.abspath(os.path.dirname(__file__))


def data_save(data, path):
    json.dump(data, open(path , 'w', encoding='utf-8'), indent=4, ensure_ascii=False)


def data_read(path):
    with open(path, 'r', encoding='utf-8') as load_f:
        load_dict = json.load(load_f)
    return load_dict


def image_saving(path, image_name, image_content):
    with open(os.path.join(path, image_name), mode='wb') as f:
        f.write(image_content)


def request_data(url, headers):
    response  = requests.get(url, headers=headers)
    response.close()
    return response


def request_data_with_param(url, params, headers):
    response  = requests.get(url, params=params, headers=headers)
    response.close()
    return response


def article_download(article_url, new_type):
    article_header =  {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': 'UOR=www.baidu.com,finance.sina.com.cn,; SINAGLOBAL=110.184.30.103_1632879150.425320; Qs_lvt_336719=1633592460; Qs_pv_336719=280876225926545700; \
            U_TRS1=000000a7.abbfee5.61aec019.50eda7e5; FSINAGLOBAL=110.184.30.103_1632879150.425320; SGUID=1647346126643_17244977;\
                vjuids=-90889587e.17ff7cd1e5b.0.32a411e180f6d; lxlrttp=1578733570; UM_distinctid=180abc9d769ae3-0b78c247243cca-17333273-1fa400-180abc9d76af8a; \
                    hqEtagMode=1; _clck=dg251c|1|f1w|0; _ga=GA1.3.82933009.1647346128; __utmz=269849203.1655300863.12.11.utmcsr=baidu|utmccn=(organic)|utmcmd=organic;\
                        __utma=269849203.82933009.1647346128.1654850670.1655300863.12; Apache=221.10.55.177_1657251301.528291;\
                            ULV=1658048899188:35:2:1:221.10.55.177_1657251301.528291:1657251301784; vjlast=1658220806',
        'if-none-match': '"62a40c8f-152dc"V=5965C31',
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


    response = request_data(article_url, article_header)
    # 自适应数据编码
    response.encoding = response.apparent_encoding
    # 数据解析
    bs = BeautifulSoup(response.text, 'html.parser')

    articles = []

    id_article = ['guonei', 'guoji', 'military', 'social']
    id_artibody =     ['tech', 'US_stock', 'stock', 'ent', 'sport', 'money']
    # 文章页面解析, 针对有两种页面， 分别处理其页面
    try:
        if new_type in id_article:
            article_body = bs.find('div', id="article")
        elif new_type in id_artibody:
            article_body = bs.find('div', id="artibody")
        ps = article_body.find_all('p')

        """ 获取新闻的文本数据 """
        for i in range(len(ps)):
            result = ps[i].text
            if result != '':
                articles.append(result.strip())
    except:
        print(f'article download failed {article_url}')

    return articles


def images_download(images_url, images_path):

    image_header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'n.sinaimg.cn',
        # 'If-Modified-Since': 'Sat, 11 Jun 2022 03:25:31 GMT',
        # 'If-None-Match': "be6191a44a8a46b709e4663b67709184",
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    }

    # 图片下载
    images_filename = []
    try:
        for image_url in images_url:
            image_url = image_url['u']
            response = request_data(image_url, image_header)

            # get image encode info
            image = response.content

            # get image name from json file
            image_name = image_url.split('/')[-1]

            # saveing the image to dir: [images]
            image_saving(images_path, image_name, image)

            images_filename.append(image_name)
    except:
        pass

    return images_filename


def comments_processing(ori_comments):
    ori_comments = ori_comments[20: -1]
    ori_comments = json.loads(ori_comments)

    try:
        newest_comments = ori_comments['result']['cmntlist']
    except:
        newest_comments = []

    try:
        hottest_comments = ori_comments['result']['hot_list']
    except:
        hottest_comments = []

    try:
        sub_comments = ori_comments['result']['threaddict']
    except:
        sub_comments = {}

    return newest_comments, hottest_comments, sub_comments


def comment_download(value):
    timestamp = int(time.time() * 1000)

    docid = value['docid']
    docid = docid.replace(":", "-")

    commentid = value['commentid']
    channel = commentid.split(':')[0]

    referer = f'https://comment5.news.sina.com.cn/comment/skin/default.html?channel={channel}&newsid={docid}&group=0'
    comment_url = 'https://comment.sina.com.cn/page/info?'

    comment_header = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cookie': 'UOR=www.baidu.com,finance.sina.com.cn,; SINAGLOBAL=110.184.30.103_1632879150.425320; Qs_lvt_336719=1633592460; \
            Qs_pv_336719=280876225926545700; U_TRS1=000000a7.abbfee5.61aec019.50eda7e5; FSINAGLOBAL=110.184.30.103_1632879150.425320; \
                SGUID=1647346126643_17244977; vjuids=-90889587e.17ff7cd1e5b.0.32a411e180f6d; lxlrttp=1578733570; \
                    UM_distinctid=180abc9d769ae3-0b78c247243cca-17333273-1fa400-180abc9d76af8a; hqEtagMode=1; _clck=dg251c|1|f1w|0;\
                        _ga=GA1.3.82933009.1647346128; __utmz=269849203.1655300863.12.11.utmcsr=baidu|utmccn=(organic)|utmcmd=organic;\
                            __utma=269849203.82933009.1647346128.1654850670.1655300863.12; Apache=221.10.55.177_1657251301.528291;\
                                ULV=1658048899188:35:2:1:221.10.55.177_1657251301.528291:1657251301784; vjlast=1658220806',
        'referer': referer,
        'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "Windows",
        'sec-fetch-dest': 'script',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    }

    newest_comments_pages = []
    hottest_comments_pages = []
    sub_comments_pages = {}

    # 初始化页面从第一页开始
    page = 1
    while True:
        params = {
            'version': '1',
            'format': 'json',
            'channel': channel,
            'newsid': docid,
            'group': '0',
            'compress': '0',
            'ie': 'utf-8',
            'oe': 'utf-8',
            'page': page,
            'page_size': '10',
            't_size': '3',
            'h_size': '3',
            'thread': '1',
            'uid': 'unlogin_user',
            'callback': f'jsonp_{str(timestamp)}',
            '_': str(timestamp),
        }

        response = request_data_with_param(comment_url, params, comment_header)
        response.encoding = 'utf-8'
        ori_comments = response.text
        # print(response.url)
        newest_comments_page, hottest_comments_page, sub_comments_page = comments_processing(ori_comments)

        newest_comments_pages.extend(newest_comments_page)
        hottest_comments_pages.extend(hottest_comments_page)
        sub_comments_pages.update({page: sub_comments_page})
        page += 1

        # 当返回当页的评论为为空，或者请求报错，就终止循环
        if newest_comments_page == []:
            break

    comments ={
                'newest_comments': newest_comments_pages,
                'hottest_comments': hottest_comments_pages,
                'sub_comments': sub_comments_pages
                }

    return comments


def frist_download(total_data_dict, data_total_all_path, images_path, new_type):
    # 首次数据下载
    with tqdm(total_data_dict.items(), desc=new_type + ' First Download', file=sys.stdout, disable=False) as total_data_dict_iterator:
        for key, value in total_data_dict_iterator:
            # 1-download article
            article_url = value['url']
            article = article_download(article_url, new_type)
            value.update({'article': article})

            # 2-download images, when images key not in value dict
            try:
                images_url = value['images']
                images_filename = images_download(images_url, images_path)
                value.update({'images_filename': images_filename})
            except:
                images_filename = []

            # 3-download comments, if  comment_show value != 0
            if int(value['comment_show']) != 0:
                comments = comment_download(value)
            else:
                comments ={
                            'newest_comments': [],
                            'hottest_comments': [],
                            'sub_comments': {}
                            }
            value.update({'comments': comments})

        data_save(total_data_dict, data_total_all_path)


def update_dict_all(data_total_all_dict, data_total_all_path, new_type):
    """
        更新请求下载, 当评论数量小于或者等于10, 进行评论更新操作
    """
    with tqdm(data_total_all_dict.items(), desc=new_type + ' Update Download', file=sys.stdout, disable=False) as data_total_all_dict_iterator:
        for key, value in data_total_all_dict_iterator:
            comment_len = len(value['comments']['newest_comments'])

            # 评论数量小于10重新请求，然后赋值
            if comment_len < 10:
                comments = comment_download(value)
                value['comments'] = comments

        # 覆盖保存 data_total_all.json文件
        data_save(data_total_all_dict, data_total_all_path)


def download(total_data_dict, data_total_all_path, images_path, new_type):
    if not os.path.exists(data_total_all_path):
        # 首次执行文章和评论下载
        frist_download(total_data_dict, data_total_all_path, images_path, new_type)
    else:
        data_total_all_dict = data_read(data_total_all_path)
        """
        需要对执行data_total_all.json操作，
        更新机制：
                (1)当 comment_show == 0 时需要执行更新操作，重新请求URL;
                (2)当 comments --> newest_comments 中评论数量小于10时，则重新请求url加载
        """
        update_dict_all(data_total_all_dict, data_total_all_path, new_type)


def main():
    main_path = os.path.join(PATH, 'Sina')
    for new_type in os.listdir(main_path):

        new_type_path = os.path.join(main_path, new_type)

        total_data_path = os.path.join(new_type_path, 'total_data.json')
        data_total_all_path =  os.path.join(new_type_path, 'data_total_all.json')

        images_path =  os.path.join(new_type_path, 'images')
        if not os.path.exists(images_path):
            os.mkdir(images_path)

        total_data_dict = data_read(total_data_path)
        download(total_data_dict, data_total_all_path, images_path, new_type)


if __name__ == '__main__':
    main()

