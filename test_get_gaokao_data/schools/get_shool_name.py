import json
import wget
import requests
import os


# # 爬取JSON文件
# try:
#     url = 'https://static-data.gaokao.cn/www/2.0/school/name.json'
#     wget.download(url=url, out='school_name.json')
# except Exception as e:
#     print(e)

url = 'https://static-data.gaokao.cn/www/2.0/school/name.json'

try:
    # 从 URL 获取 JSON 数据
    response = requests.get(url)
    data = response.json()

    # 写入 JSON 文件，启用 ensure_ascii=True 来转义非 ASCII 字符
    with open('school_name.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

except Exception as e:
    print(e)





