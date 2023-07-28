from copy import deepcopy
from hashlib import new
from heapq import merge
import json
from multiprocessing.sharedctypes import Value
import os
from sre_constants import REPEAT_ONE
from tempfile import tempdir
from tqdm import tqdm
import sys
from collections import Counter
import numpy as np
import re
import jieba
from datetime import datetime,date
import numpy as np


PATH = os.path.abspath(os.path.dirname(__file__))


def data_save(data, path):
    json.dump(data, open(path , 'w', encoding='utf-8'), indent=4, ensure_ascii=False)


def data_read(path):
    with open(path, 'r', encoding='utf-8') as load_f:
        load_dict = json.load(load_f)
    return load_dict


def train_data(Netease_dcit):
    datas = {}

    with tqdm(Netease_dcit.items(), desc=' Filter', file=sys.stdout, disable=False) as Netease_dcit_iterator:
        for key, value in Netease_dcit_iterator:
            # selction the comment
            comments_text = set()
            comments = value['comment']['newList']['comments']
            for i in comments:
                comment_text = comments[i]['content']
                comments_text.add(comment_text)
            comments_text = list(comments_text)

            data = {
                # 'title': value['title'],
                # 'label': value['label'],
                # 'content': value['content'],
                'comments': comments_text,
            }

            datas.update({key: data})

    data_save(datas, os.path.join(PATH, 'Netease-comment.json'))


def article_len_statistics(Netease_dcit):
    with tqdm(Netease_dcit.items(), desc=' Filter', file=sys.stdout, disable=False) as Netease_dcit_iterator:
        article_len = []
        sentence_lens = []

        for key, value in Netease_dcit_iterator:
            if value['content'] != None:
                article = value['content']
                sentence_len = 0
                for sentence in article:
                    sentence_len += len(sentence)
                sentence_lens.append(sentence_len)

        print('mean_len', np.mean(sentence_lens))
        print('median_len', np.median(sentence_lens))
        print(Counter(sentence_lens))


class ProcessingComment():
    def __init__(self) -> None:
        super(ProcessingComment, self).__init__()
        # comment_path = os.path.join(PATH, 'Netease-comment.json')
        # self.comment_dcit = data_read(comment_path)
        self.RepeatNum = 0

    def filtering_rule(self, sentence):
        # 逗号
        sentence = re.sub(r'，{2,}', r'，', sentence)
        sentence = re.sub(r',{2,}', r',', sentence)

        # 句号
        sentence = re.sub(r'。{2,}', r'。', sentence)
        sentence = re.sub(r'\.{2,}', r'.', sentence)

        # 问号
        sentence = re.sub(r'？{2,}', r'？', sentence)
        sentence = re.sub(r'\?{2,}', r'?', sentence)

        # 感叹号
        sentence = re.sub(r'！{2,}', r'！', sentence)
        sentence = re.sub(r'!{2,}', r'!', sentence)

        # 冒号
        sentence = re.sub(r'：{2,}', r'：', sentence)
        sentence = re.sub(r':{2,}', r':', sentence)

        # 分号
        sentence = re.sub(r'；{2,}', r'；', sentence)
        sentence = re.sub(r';{2,}', r';', sentence)

        # 顿号
        sentence = re.sub(r'、{1,}', r'、', sentence)

        # 括号
        sentence = re.sub(r'（{2,}', r'（', sentence)
        sentence = re.sub(r'）{2,}', r'）', sentence)
        sentence = re.sub(r'\({2,}', r'(', sentence)
        sentence = re.sub(r'\){2,}', r')', sentence)

        sentence = re.sub(r'【{2,}', r'【', sentence)
        sentence = re.sub(r'】{2,}', r'】', sentence)
        sentence = re.sub(r'\[{2,}', r'[', sentence)
        sentence = re.sub(r']{2,}', r']', sentence)

        sentence = re.sub(r'\{{2,}', r'{', sentence)
        sentence = re.sub(r'}{2,}', r'}', sentence)

        sentence = re.sub(r'\\{2,}', r'\\', sentence)

        sentence = re.sub(r'\|{2,}', r'|', sentence)

        sentence = re.sub(r'/{2,}', r'/', sentence)

        # 破折号
        sentence = re.sub(r'\-{1,}', r'-', sentence)
        sentence = re.sub(r'—{1,}', r'-', sentence)

        # 省略号
        sentence = re.sub(r'…{1,}', r'-', sentence)

        # 书名号
        sentence = re.sub(r'《{2,}', r'《', sentence)
        sentence = re.sub(r'》{2,}', r'》', sentence)
        sentence = re.sub(r'<{2,}', r'<', sentence)
        sentence = re.sub(r'>{2,}', r'>', sentence)

        # 特殊符号
        sentence = re.sub(r'%{2,}', r'%', sentence)

        sentence = re.sub(r'@{2,}', r'@', sentence)

        sentence = re.sub(r'#{2,}', r'#', sentence)

        sentence = re.sub(r'￥{2,}', r'￥', sentence)
        sentence = re.sub(r'\${2,}', r'$', sentence)

        sentence = re.sub(r'&{2,}', r'&', sentence)


        sentence = re.sub(r'\^{1,}', r'', sentence)

        sentence = re.sub(r'\*{1,}', r'', sentence)

        sentence = re.sub(r'_{1,}', r'', sentence)

        sentence = re.sub(r'={1,}', r'', sentence)

        sentence = re.sub(r'\+{1,}', r'', sentence)

        # 替换 \n \r \t
        sentence = sentence.replace('\n', '')
        sentence = sentence.replace('\r', '')
        sentence = sentence.replace('\\n', '')
        sentence = sentence.replace('\\r', '')

        sentence = sentence.replace('\t', '')

        sentence = sentence.replace('「', '')
        sentence = sentence.replace('」', '')

        sentence = sentence.replace('. ', '')
        sentence = sentence.replace('。 ', '')

        sentence = sentence.replace('┏', '')
        sentence = sentence.replace('┓', '')

        sentence = sentence.replace('🫡', '')

        sentence = sentence.replace('●', '')
        sentence = sentence.replace('°', '')
        sentence = sentence.replace('◆', '')
        sentence = sentence.replace('■', '')
        sentence = sentence.replace('. ', '')

        sentence = sentence.replace('. ', '')

        sentence = re.sub(r'　{1,}', r'', sentence)



        # 去掉空格
        sentence = re.sub(r'^ {1,}', r' ', sentence)
        sentence = re.sub(r' {1,}$', r' ', sentence)

        return sentence

    def filter_repeat_sentence(self, comments):
        """
        去除list中重复的内容
        """
        list_len, set_len = len(comments), len(set(comments))

        # 若list的长度和集合长度不一致，说明存在重复的句子，利用set去重然后根据 list 的index 的
        if list_len != set_len:
            comments = sorted(set(comments), key=comments.index)
            self.RepeatNum += 1

        return comments

    def filter_subset_comment(self, comments):
        new_comments = deepcopy(comments)

        for short_sentence, _ in comments.items():
            for long_sentence, _  in comments.items():
                if not short_sentence == long_sentence:
                    if short_sentence in long_sentence and len(short_sentence) >= 5:
                        try:
                            # 由于首次符合该条件的句子已经被删除了，而后续句子还是人家子集句子，删除报错
                            del new_comments[short_sentence]
                            # print(short_sentence)
                        except:
                            # print(short_sentence, 'not is exist!!!')
                            pass

        return new_comments

    def filter_comment_min_len(self, comment):
        """
        按最小长度过滤评论
        """
        if len(comment) < 5:
            comment = None

        return comment

    def filter_comment_max_len(self,comments):
        new_comments = deepcopy(comments)

        for sentence, _  in comments.items():
            sentence_list = sentence.split(' ')
            if len(sentence_list) > 60 :
                del new_comments[sentence]

        return new_comments

    def segmentation(self, comment):
        # 进行分词操作
        segmentation_comment = jieba.cut(comment, cut_all=False)
        segmentation_comment = " ".join(segmentation_comment)

        return segmentation_comment

    def post_processing(self, comment):
        filter_comment = re.sub(r' {1,}', r' ', comment)

        return filter_comment

    def get_N_longest_comment(self, comments):
        """
        获取评论中长度前 10 的文本
        """
        new_comments = {}

        comment_contents = list(comments.keys())
        comment_contents = sorted(comment_contents, key = lambda i:len(i), reverse=True)
        comment_contents = comment_contents[:10]

        for new_key in comment_contents:
            value = comments[new_key]
            new_comments.update({new_key: value})

        return new_comments

    def filter_comment_content(self, comments_dict):
        """ 处理单条评论 """
        new_comments = {}

        for key, value in comments_dict.items():
            # 去掉评论中<br>标签
            content = value['content']
            content = re.sub(r'<br>|<br>[0-9]|br', '', content)

            # 处理标点符号重复问题
            content = self.filtering_rule(content)

            # 对评论文本的最小长度做限制
            content = self.filter_comment_min_len(content)

            # 抛弃过滤后为空的评论
            if content != None:
                # 对评论分词
                content = self.segmentation(content)

                # 评论内容后处理
                content = self.post_processing(content)

            value['content'] = content
            new_comments.update({key: value})

        return new_comments


class ProcessingArticle(object):
    def __init__(self) -> None:
        # article_path = os.path.join(PATH, 'Netease-article.json')
        # self.article_dcit = data_read(article_path)

        self.Chars = set()
        self.RepeatNum = 0

        self.total_article_len = 0
        self.total_article_sentence_num = 0
        self.total_article_sentence_len = 0

    def statistical_char(self, new_article):
        for sentence in new_article:
            for char in sentence:
                self.Chars.add(char)

    def statistical_article_lenth(self, new_article):
            self.total_article_len += len(new_article[-1])
            pass

    def statistical_article_sentence_num(self, new_article):
            self.total_article_sentence_num += len(new_article)
            pass

    def statistical_article_sentence_len(self, new_article):
            single_article_len = 0
            for sentence in new_article:
                single_article_len += len(sentence)

            if new_article != []:
                self.total_article_sentence_len = single_article_len // len(new_article)
                pass

    # ----------------------

    def sentence_split(self, article):
        """
        中文句子划分标识：
        """
        # (1) 。
        new_article = []
        for sentence in article:
            sentence_list = sentence.split('。')
            sentence_list = [item + '。' for item in sentence_list]
            new_article.extend(sentence_list)

        # # (2) ？
        # article = new_article
        # new_article = []
        # for sentence in article:
        #     if '？' in sentence:
        #         sentence_list = sentence.split('？')
        #         sentence_list_add_mark = [sentence_list[i] + '？' for i in range(len(sentence_list) - 1)]
        #         sentence_list_add_mark.append(sentence_list[-1])
        #         new_article.extend(sentence_list_add_mark)
        #     else:
        #         new_article.append(sentence)

        # # (3) ！
        # article = new_article
        # new_article = []
        # for sentence in article:
        #     if '！' in sentence:
        #         sentence_list = sentence.split('！')
        #         sentence_list_add_mark = [sentence_list[i] + '！' for i in range(len(sentence_list) - 1)]
        #         sentence_list_add_mark.append(sentence_list[-1])
        #         new_article.extend(sentence_list_add_mark)
        #     else:
        #         new_article.append(sentence)

        # 对文章清洗，当面对标点符号独自占据一行时
        punctuation = ['。', '？', '！']
        for sentence in new_article:
            if sentence in punctuation:
                try:
                    new_article.remove(sentence)
                except:
                    pass

        # 对评论长度的下限做限制
        for sentence in new_article:
            if len(sentence) < 5 :
                new_article.remove(sentence)

        return new_article

    def article_len_statistics(self, Netease_dcit):
        with tqdm(Netease_dcit.items(), desc=' Filter', file=sys.stdout, disable=False) as Netease_dcit_iterator:
            article_len = []
            sentence_lens = []

            for key, value in Netease_dcit_iterator:
                if value['content'] != None:
                    article = value['content']
                    sentence_len = 0
                    for sentence in article:
                        sentence_len += len(sentence)
                    sentence_lens.append(sentence_len)

            print('mean_len', np.mean(sentence_lens))
            print('median_len', np.median(sentence_lens))
            print(Counter(sentence_lens))

    def filter_keywords(self, keywords, sentence):
        flag = False
        for item in keywords:
            if item in sentence and len(sentence) < 60:
                flag = True

        return flag

    def filter_subset_sentence(self, new_article):
        """
        过滤掉list中其他包含其他位置子集内容
        """
        filter_subset_article = deepcopy(new_article)

        for short_sentence in new_article:
            for long_sentence in new_article:
                if not short_sentence == long_sentence:
                    if short_sentence in long_sentence and len(short_sentence) > 30:
                        try:
                            # 由于首次符合该条件的句子已经被删除了，而后续句子还是该子集句子，删除报错
                            filter_subset_article.remove(short_sentence)
                        except:
                            # print(short_sentence, 'not is exist!!!')
                            pass

        return filter_subset_article

    def filtering_rule(self, sentence):
        """ 统一采用中文的标点符号 """
        # 英文标点转中文标点 ！ ？， {2,}采用从1匹配

        # 逗号
        sentence = re.sub(r'，{1,}', r'，', sentence)
        sentence = re.sub(r',{1,}', r'，', sentence)

        # 句号
        sentence = re.sub(r'。{1,}', r'。', sentence)
        sentence = re.sub(r'\.{1,}', r'.', sentence)

        # 问号
        sentence = re.sub(r'？{1,}', r'？', sentence)
        sentence = re.sub(r'\?{1,}', r'？', sentence)

        # 感叹号
        sentence = re.sub(r'！{1,}', r'！', sentence)
        sentence = re.sub(r'!{1,}', r'！', sentence)

        # 冒号
        sentence = re.sub(r'：{1,}', r'：', sentence)
        sentence = re.sub(r':{1,}', r'：', sentence)

        # 分号
        sentence = re.sub(r'；{1,}', r'；', sentence)
        sentence = re.sub(r';{1,}', r'；', sentence)

        # 顿号
        sentence = re.sub(r'、{1,}', r'、', sentence)

        # 括号
        sentence = re.sub(r'（{1,}', r'（', sentence)
        sentence = re.sub(r'）{1,}', r'）', sentence)
        sentence = re.sub(r'\({1,}', r'（', sentence)
        sentence = re.sub(r'\){1,}', r'）', sentence)

        sentence = re.sub(r'【{1,}', r'\[', sentence)
        sentence = re.sub(r'】{1,}', r']', sentence)
        sentence = re.sub(r'\[{1,}', r'\[', sentence)
        sentence = re.sub(r']{1,}', r']', sentence)

        sentence = re.sub(r'\{{1,}', r'{', sentence)
        sentence = re.sub(r'}{1,}', r'}', sentence)

        sentence = re.sub(r'\\{1,}', r'\\', sentence)

        sentence = re.sub(r'\|{1,}', r'|', sentence)

        sentence = re.sub(r'/{1,}', r'/', sentence)

        # 破折号
        sentence = re.sub(r'\-{1,}', r'-', sentence)
        sentence = re.sub(r'—{1,}', r'-', sentence)


        # 省略号
        sentence = re.sub(r'…{1,}', r'-', sentence)

        # 书名号
        sentence = re.sub(r'《{1,}', r'《', sentence)
        sentence = re.sub(r'》{1,}', r'》', sentence)
        sentence = re.sub(r'<{1,}', r'<', sentence)
        sentence = re.sub(r'>{1,}', r'>', sentence)

        # 特殊符号
        sentence = re.sub(r'%{1,}', r'%', sentence)

        sentence = re.sub(r'@{1,}', r'@', sentence)

        sentence = re.sub(r'#{1,}', r'#', sentence)

        sentence = re.sub(r'￥{1,}', r'￥', sentence)
        sentence = re.sub(r'\${1,}', r'$', sentence)

        sentence = re.sub(r'&{1,}', r'&', sentence)


        sentence = re.sub(r'\^{1,}', r'', sentence)

        sentence = re.sub(r'\*{1,}', r'', sentence)

        sentence = re.sub(r'_{1,}', r'', sentence)

        sentence = re.sub(r'={1,}', r'', sentence)

        sentence = re.sub(r'\+{1,}', r'', sentence)

        # 替换 \n \r \t
        sentence = sentence.replace('\n', '')
        sentence = sentence.replace('\r', '')
        sentence = sentence.replace('\\n', '')
        sentence = sentence.replace('\\r', '')

        sentence = sentence.replace('\t', '')

        sentence = sentence.replace('「', '')
        sentence = sentence.replace('」', '')

        # 去掉空格
        sentence = re.sub(r' {1,}', r' ', sentence)

        # 移除不可见的字符
        new_sentence = []
        for item in sentence:
            is_printable_char = item.isprintable()
            if is_printable_char:
                new_sentence.append(item)

        sentence = ''.join(new_sentence)

        return sentence

    def filter_article_content(self, article):
        new_article = []

        for sentence in article:
            sentence = self.filtering_rule(sentence)

            if sentence != '':
                new_article.append(sentence)

        return new_article

    def filter_repeat_sentence(self, article):
        """
        去除list中重复的内容
        """
        list_len, set_len = len(article), len(set(article))

        # 若list的长度和集合长度不一致，说明存在重复的句子，利用set去重然后根据 list 的index 的
        if list_len != set_len:
            article = sorted(set(article), key=article.index)
            self.RepeatNum += 1

        return article

    def add_extra_punctuation(self, article):
        """
        list中每个句子是否都带有标点符号，方便后续句子切分

        """
        punctuation = ['。', '.',
                    '，', ',',
                    '！', '!',
                    '、',
                    '；', ';',
                    '：', ':',
                    '？', '?',
                    ]

        new_article = []

        # 针对filter_subset_article 中list一行没有标点分割符号，额外添加
        for index, sentence in enumerate(article):

            # 获得元素中每个句子中最后的字符
            end_char = sentence[-1]

            if end_char in punctuation:
                # 若存在给定字符集中，不做处理
                # print(end_char)
                pass
            else:
                # 若是list中最后一个元素，则赋值为句号，否则赋值为逗号
                if index != len(article) - 1:
                    sentence += '，'
                else:
                    sentence += '。'
            new_article.append(sentence)

        return new_article

    def segmentation(self, article):
        # 进行分词操作
        segmentation_article = []

        for sentence in article:
            sentence = jieba.cut(sentence, cut_all=False)
            sentence = " ".join(sentence)
            segmentation_article.append(sentence)

        return segmentation_article

    def post_processing(self, article):
        post_keywords = [
            '（中新财经）', '搜索，复制', '（布布）', '（奋斗乌托邦/文）', '（海外网', '（总台记者', '（央视记者', '（专栏作家）',\
            '（参与记者', '（编译', '（声明：', '（备注：', '（文猛）', '（唐风）', '（作者', '（总台央视记者', '（佟恒）', '（伊万）',\
            '（塞尔吉奥）', '（斯科）', '（茉莉）', '（文玄）', '（卡卡）', '（棋牌深度报道组', '（胡波）', '（小风）', '排版：',\
            '（清泠）', '（佳佳）', '（二饼）', '摄影：', '（澎湃新闻记者', '（福布斯）', '视觉中国）', '（子健）', '（星海）',\
            '（澎湃新闻记者', '（法律学者）', '（文中受访', '（总台记者', '（参与记者', '（顾锦东）', '（李晓）', '（江雪）', '（柳玉鹏）',\
            '（中新经纬APP）', '编撰/', '（应受访者要求', '设计：', '（中青报', '（人民日报）', '（编辑/', '（中新经纬APP）', '监  制：',\
            '（刘旭）', '作者/', '（央视新闻）',
        ]

        for sentence in article:
            if len(sentence) < 30:
                for item in post_keywords:
                    if item in sentence:
                        try:
                            article.remove(sentence)
                        except:
                            # print(sentence)
                            pass

        return article

    def filter_article_text(self, article):
        # 初始化 新的文章列表
        new_article = []
        filter_content = []

        keywords = ['|', '｜', 'https', 'https://', 'http', 'http://', '丨', '版权声明', '免责声明', '未经许可', '未经授权', '授权转载合作联系人', \
        '▲', '△', '图 源丨', '图源：','图源/', '新媒体排版', 'END',\
        '编辑：', '编 辑丨', '编辑/', '责编：', '编辑 ', '责编', '主编', '主编|', '作者：', '作 者丨', '作者丨', '作者|','编 辑丨', '编辑／', '本期编辑', '见习记者 ', \
        '（原标题：', '文丨', '文 |', '文/', '文：', '资料图', '公众号：', '新浪微博 /', '封面图片：', '转载请注明',
        '出品|', '华商韬略', '部分图片来源于网络', '如涉及侵权', '版权所有', '请联系删除', '原创文章', '如有侵权', '如需转载', '侵权必究', \
        '本文来源：', '来源:', '图片来源', '图源网络', '原文标题：', '图片源于网络', '应采访对象要求', '校对：', '监制：', '中国基金报', '作者：',\
        ]

        # 去掉含有无用关键字的句子
        for sentence in article:
            # 匹配 XXX 记者类
            match_journalist = re.match(r'^.*?记者 |^.*?记者：|^.*?财经 |^.*?财经出品 |^.*?来源：|网易体育.*?报道', sentence)

            # 匹配 [1] ....，参考引用型句子
            matchObj = re.match(r'\[\d\]|（原标题：|^（编辑', sentence)

            # 过滤掉url
            Url_obj = re.compile(r'[a-zA-z]+://[^\s]*')
            url = Url_obj.findall(sentence)

            # 过滤 邮箱
            E_mail_obj = re.compile(r"[\w!#$%&'*+/=?^_`{|}~-]+(?:\.[\w!#$%&'*+/=?^_`{|}~-]+)*@(?:[\w](?:[\w-]*[\w])?\.)+[\w](?:[\w-]*[\w])?")
            e_mail = E_mail_obj.findall(sentence)

            # 过滤 电话号码
            Phone_num = re.compile(r"\d{3}-\d{8}|\d{4}-\{7,8}")
            phone_num = Phone_num.findall(sentence)

            # 1. 去掉为空的句子
            if len(sentence) == 0:
                continue

            # 2. 去掉 记者 XXX
            elif match_journalist:
                if len(sentence) <=60:
                    # 匹配成功但小于 60则过滤掉
                    # print(sentence)
                    filter_content.append(sentence)
                    pass
                else:
                    # 将匹配成功的句子大于60的直接添加到 新文章列表中
                    new_article.append(sentence)

            elif url != []:
                # print(sentence)
                continue

            elif e_mail != []:
                # print(sentence)
                continue

            elif phone_num != []:
                # print(sentence)
                continue

            else:
                # 3. 二次正则表达式过滤
                if matchObj:
                    # 匹配成功则过滤掉该句子
                    filter_content.append(sentence)
                    # print(sentence)
                    pass

                else:
                    # 4. 判断该句子是否还存在keywords关键指定的内容，有则过滤
                    flag = self.filter_keywords(keywords, sentence)
                    if not flag:
                        new_article.append(sentence)
                    else:
                        filter_content.append(sentence)
                        # print(sentence)

        # 去掉重复的句子
        new_article = self.filter_repeat_sentence(new_article)

        # 去掉含有包含关系的句子，即去掉子集句子
        new_article = self.filter_subset_sentence(new_article)

        # 内容过滤,
        new_article = self.filter_article_content(new_article)

        # 增加额外的标点符号
        new_article = self.add_extra_punctuation(new_article)

        # 合并为一段文档
        new_article = [''.join(new_article)]

        # 句子层级划分
        new_article = self.sentence_split(new_article)

        # 后处理去掉之前处理不掉的关键词
        new_article = self.post_processing(new_article)

        # 分词操作
        new_article = self.segmentation(new_article)

        return new_article, filter_content

    def forword(self, ):
        filter_contents = []
        datas = {}

        for key, value in self.article_dcit.items():
            article = value['content']
            if article != None:
                new_article, filter_content = self.filter_article_text(article)

                data = {'content': new_article}
                datas.update({key: data})

                # 存留 过滤句子和字符
                filter_contents.extend(filter_content)


        print('repeat sentence number', self.RepeatNum)
        print('total article number', len(datas))
        print(f'article average length { self.total_article_len / len(datas)}')
        print(f'article sentence average number { self.total_article_sentence_num / len(datas)}')
        print(f'article sentence average length { self.total_article_sentence_len / len(datas)}')
        # print('Char:', self.Chars)

        # data_save(datas, os.path.join(PATH, 'NeteaseFilterArticle.json'))
        # data_save(list(set(filter_contents)), os.path.join(PATH, 'NeteaseFilterContent.json'))


class Processing():
    def __init__(self) -> None:
        # Sina_userinfo 第一次完整跑完所有流程并绘制可视化图像的数据集，并不作为后期训练所使用的数据集。
        self.main_path = os.path.join(PATH, 'Sina_userinfo')

        self.Sina = {}
        self.age_frequency = []
        self.gender_frequency = []
        self.location_frequency = []

        self.processingarticle = ProcessingArticle()
        self.processingcomment = ProcessingComment()

    def processing_article_text(self, article):
        new_article, _ = self.processingarticle.filter_article_text(article)

        # 若内容为空则返回None
        if len(new_article) == 0:
            new_article = None

        return new_article

    def processing_title_text(self, title):
        title.replace(' ', '')

        title = jieba.cut(title, cut_all=False)
        title = " ".join(title)

        return title

    def processing_keywords(self, keywords):
        keywords = keywords.split(',')
        new_keywords = []

        for item in keywords:
            if item != '':
                new_keywords.append(item)
        return new_keywords

    def get_comment_other_info(self, comments_dict):
        """
        点赞数量 vote
        点踩数量 against
        用户信息 user
            用户昵称 nickname
            用户位置 location
            用户头像  avatar
            头衔等级 titleinfo
        """
        new_comments_dict = {}

        for sentence, value in comments_dict.items():
            # 先判断是否存在这些字段，没有则赋值初始化的值
            if 'vote' in value:
                vote = value['vote']
            else:
                vote = 0

            if 'against' in value:
                against = value['against']
            else:
                against = 0

            content = value['content']

            # 初始化 user
            user = {}
            if 'user' in value:
                if 'nickname' in value['user']:
                    nickname = value['user']['nickname']
                else:
                    nickname = ''

                if 'location' in value['user']:
                    location = value['user']['location']
                else:
                    location = ''

                if 'avatar' in value['user']:
                    avatar = value['user']['avatar']
                else:
                    avatar = ''

                if 'titleinfo' in value['user']:
                    titleinfo = value['user']['titleinfo']
                else:
                    titleinfo = ''

                user.update({'nickname': nickname})
                user.update({'location': location})
                user.update({'avatar': avatar})
                user.update({'titleinfo': titleinfo})


            new_value = {'vote': vote,
                        'against': against,
                        'content': content,
                        'user': user
                        }

            new_comments_dict.update({sentence: new_value})

        return new_comments_dict

    def calculate_age(self, born):
        # 给定具体的出生日期计算年龄
        today = date.today()
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        return age

    def processing_birthday(self, birthday):
        # 防止 月 日为00-00的情况，初始化为01-01
        years_month_day = birthday.split('-')
        years = years_month_day[0]
        month = years_month_day[1]
        day = years_month_day[-1]
        if month == '00':
            month = '01'
        if day == '00':
            day = '01'
        birthday = '-'.join([years, month, day])

        return birthday

    def processing_userinfo(self, comment):
        for key, value in comment.items():

            # 1. 处理 birthday， 目标 数字年龄
            birthday = value['userinfo']['birthday'].split(' ')[0]

            # 将非出生日期的排除
            if len(birthday) > 3:
                birthday = self.processing_birthday(birthday)

                birth_date = datetime.strptime(birthday, '%Y-%m-%d')
                age = self.calculate_age(birth_date)

                # 将年龄范围限制到 1-100之间，把符合要求的添加年龄字段
                if age > 0 and age < 100:
                    self.age_frequency.append(age)
                    value['userinfo'].update({'age': age})

            # 2. 处理 gender， 三分类， m, f o
            gender = value['userinfo']['gender']

            if gender in ['m', 'f']:
                self.gender_frequency.append(gender)
            else:
                value['userinfo']['gender'] = ''

            # 3. 处理 location, 只限制具体省，不显示具体城市，
            location = value['userinfo']['location'].split(' ')[0]
            value['userinfo']['location'] = location
            if location != '':
                self.location_frequency.append(location)

            # 4. 对 description 分词
            description = value['userinfo']['description']
            description = jieba.cut(description, cut_all=False)
            description = " ".join(description)
            value['userinfo']['description'] = description

        return comment

    def processing_comments(self, comments):
        # 处理 comemnt
        new_comments = []

        for comment in comments:
            # 对评论数据进行过滤
            comment = self.processingcomment.filter_comment_content(comment)

            # 处理附加属性字段
            comment = self.processing_userinfo(comment)

            # 若 comment['content'] 为 None, 则在 comments 中抛弃掉该评论
            content = list(comment.values())[0]['content']
            if content != None:
                new_comments.append(comment)

        # 若 过滤后 comments 内无评论数据，则返回一个 []
        return new_comments

    def processing_images(self, images):
        new_images = []
        for item in images:
            image = item['u']
            new_images.append(image)
        return new_images

    def age_default(self):
        # 统计年龄分布，补充缺失值
        age_frequency_dict = dict(Counter(self.age_frequency))

        # 获得 numpy 格式的 age 和 frequency 数据
        age = []
        probability = []
        freq_total = sum(age_frequency_dict.values())
        for key, value in age_frequency_dict.items():
            age.append(key)
            probability.append(value/freq_total)
        age = np.array(age)
        probability = np.array(probability)

        check_age = []

        with tqdm(self.Sina.items(), desc='Sina userinfo attribute age default', file=sys.stdout, disable=False) as Sina_dict_iterator:
            for key, value in Sina_dict_iterator:
                comments = value['comments']

                for comment in comments:
                    for comment_key, comment_value in comment.items():
                        if 'age' not in comment_value['userinfo']:
                            # 使用numpy进行按概率分布进行采样，获得一个默认值
                            choice_age = int(list(np.random.choice(a=age, size=1, replace=True, p=probability))[0])
                            comment_value['userinfo'].update({'age': choice_age})
                        check_age.append(comment_value['userinfo']['age'])

        print(Counter(check_age))

    def gender_default(self):
        gender_frequency_dict = dict(Counter(self.gender_frequency))

        # 获得 numpy 格式的 gender 和 frequency 数据
        gender = []
        probability = []
        freq_total = sum(gender_frequency_dict.values())
        for key, value in gender_frequency_dict.items():
            gender.append(key)
            probability.append(value/freq_total)

        check_gender = []
        with tqdm(self.Sina.items(), desc='Sina userinfo attribute gender default', file=sys.stdout, disable=False) as Sina_dict_iterator:
            for key, value in Sina_dict_iterator:
                comments = value['comments']

                for comment in comments:
                    for comment_key, comment_value in comment.items():
                        if comment_value['userinfo']['gender'] not in ['f', 'm']:
                            # 使用numpy进行按概率分布进行采样，获得一个默认值
                            choice_gender = list(np.random.choice(a=gender, size=1, replace=True, p=probability))[0]
                            comment_value['userinfo']['gender'] = choice_gender

                        check_gender.append(comment_value['userinfo']['gender'])

        print(Counter(check_gender))

    def location_default(self):
        location_frequency_dict = dict(Counter(self.location_frequency))

        # 获得 numpy 格式的 gender 和 frequency 数据
        location = []
        probability = []
        freq_total = sum(location_frequency_dict.values())
        for key, value in location_frequency_dict.items():
            location.append(key)
            probability.append(value/freq_total)

        i = 0
        check_location = []

        with tqdm(self.Sina.items(), desc='Sina userinfo attribute location default', file=sys.stdout, disable=False) as Sina_dict_iterator:
            for key, value in Sina_dict_iterator:
                comments = value['comments']

                for comment in comments:

                    i += 1

                    for comment_key, comment_value in comment.items():
                        if comment_value['userinfo']['location'] == '':
                            # 使用numpy进行按概率分布进行采样，获得一个默认值
                            choice_location = list(np.random.choice(a=location, size=1, replace=True, p=probability))[0]
                            comment_value['userinfo']['location'] = choice_location

                        check_location.append(comment_value['userinfo']['location'])

        print(Counter(check_location))
        print('total comment number',i)

    def release_data(self, Sina_filter_attribute_dict):
        """
        数据集的处理标准：只保留文章和评论均不空的数据
        由于受到内存的限制，所以尽可能不要开辟新的存储单元，应尽量采用原有变量
        """

        with tqdm(Sina_filter_attribute_dict.items(), desc='Sina userinfo', file=sys.stdout, disable=False) as type_data_dict_iterator:
            for key, value in type_data_dict_iterator:
                title = value['title']
                images = value['images']
                keywords = value['keywords']
                comments = value['comments']

                # 处理新闻内容，过滤掉不要的内容
                # ... 单独开辟函数写过滤表达式
                article = value['content']

                # 处理 image 仅保留url
                images = self.processing_images(images)

                # 处理文章内容
                article = self.processing_article_text(article)

                # 处理 title
                title = self.processing_title_text(title)

                # # 处理 keywords
                keywords = self.processing_keywords(keywords)

                # # 处理评论内容
                comments = self.processing_comments(comments)

                # 跳过 文章内容为空
                if article == None or article == []:
                    # print('article is None or is []', key)
                    continue

                # 跳过 评论集为空的
                if comments == None or comments == []:
                    # print('comments is None or is []', key)
                    continue

                # 当 文章 与 评论 都不为空时则保存数据
                if article != None and comments != []:
                    value['images'] = images
                    value['keywords'] = keywords
                    value['comments'] = comments
                    value['content'] = article
                    value['title'] = title

                    self.Sina.update({key: value})
                else:
                    pass

    def forward(self, ):
        Sina_filter_attribute_path = 'Sina/Sina_filter_attribute_712k.json'
        # path name processing
        Sina_path_list = Sina_filter_attribute_path.split('/')
        sub_path = Sina_path_list[0]
        num = Sina_path_list[-1].split('.')[0].split('_')[-1]
        Sina_save_path = os.path.join(PATH, sub_path, f'Sina_{num}.json')

        Sina_filter_attribute_dict = data_read(Sina_filter_attribute_path)

        self.release_data(Sina_filter_attribute_dict)

        # 对 补充缺失值
        self.age_default()
        self.gender_default()
        self.location_default()

        # 保存数据
        data_save(self.Sina, Sina_save_path)

def main():
    processing = Processing()
    processing.forward()


if __name__ == '__main__':
    main()

