import json
import sys
from tqdm import tqdm

import datetime
# 打印当前时间
time2 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(time2)


def data_read(path):
    with open(path, 'r', encoding='utf-8') as load_f:
        load_dict = json.load(load_f)
    return load_dict

path = 'Sina/money/data_total_all.json'

data_total_all_dict = data_read(path)

with tqdm(data_total_all_dict.items(), file=sys.stdout, disable=False) as total_data_dict_iterator:
    for i, (key, value) in enumerate(total_data_dict_iterator):
        if 'comments' not in value:
            print(i)
