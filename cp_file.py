import shutil
import os



def main(path):
    path_userinfo = './Sina_userinfo'

    categories = ['ent', 'guoji', 'guonei', 'military', 'money', 'social', 'sport', 'stock', 'tech', 'US_stock']
    files = ['total_data.json', 'data_total_all.json', 'data_total_all_userinfo.json']


    for item in categories:
        for file in files:
            path_file = os.path.join(path, item, file)

            path_userinfo_file = os.path.join(path_userinfo, item)

            if not os.path.exists(path_userinfo_file):
                os.makedirs(path_userinfo_file)

            shutil.copy(path_file, path_userinfo_file)
            pass


if __name__ == '__main__':
    path = './Sina'
    main(path)