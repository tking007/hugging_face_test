import requests
import json
import time


all_data = []  # 存储所有数据的列表

for i in range(1, 28):
    url = 'https://api.eol.cn/web/api/?keyword=&level1=1&level2=&level3=&page=' + str(i) + '&size=30&sort=&uri=apidata/api/gkv3/special/lists&signsafe=f5dd409955e7466945d1ea8145fc348e'

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',  # 自定义 User-Agent
    }

    response = requests.post(url, headers=headers)

    if response.status_code == 200 and response.json()['code'] == '0000':
        data = response.json()['data']['item']  # 直接提取每个页面的学校数据列表
        all_data.extend(data)  # 将每个页面的数据列表扩展到all_data中
        print(f'Downloaded page {i}.')
    else:
        print(f'Failed to download page {i}. Status code: {response.status_code}')

    time.sleep(5)  # 休眠5秒，防止被封IP

# 将合并后的数据保存到一个文件
merged_data = {'code': '0000', 'message': '成功---success', 'data': all_data}

with open('specials_lists.json', 'w', encoding='utf-8') as file:
    json.dump(merged_data, file, ensure_ascii=False, indent=4)

print('All data downloaded and merged into rank_list_merged.json.')
