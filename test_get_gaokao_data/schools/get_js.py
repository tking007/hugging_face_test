import requests
import json
import codecs

# url = "https://www.gaokao.cn/static/js/2024_02_26_11_13.f748a5fcc1d78b6cdefe.main~21833f8f.chunk.js"
#
# response = requests.get(url)
#
# # 确保请求成功
# if response.status_code == 200:
#     content = response.content.decode('utf-8')  # 解码响应内容
#
#     # 将Unicode转义序列转换为对应的字符
#     content = codecs.decode(content, 'unicode_escape')
#
#     with open('get_school_info.js', 'w', encoding='utf-8') as f:
#         f.write(content)


# url_2 = "https://static-data.gaokao.cn/www/2.0/school/list_v2.json"
# response_2 = requests.get(url_2)
#
# if response_2.status_code == 200:
#     data = response_2.json()
#
#     with open('list_v2.json', 'w', encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False, indent=4)

url_3 = "https://www.gaokao.cn/static/js/2024_02_26_11_13.f748a5fcc1d78b6cdefe.main~21833f8f.chunk.js"
response_3 = requests.get(url_3)

if response_3.status_code == 200:
    content = response_3.content.decode('utf-8')

    content = codecs.decode(content, 'unicode_escape')

    with open('college_level.js', 'w', encoding='utf-8') as f:
        f.write(content)