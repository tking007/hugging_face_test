import json
import requests
import time

with open('specials_lists.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

for major in data['data']:
    special_id = major.get('special_id')
    special_url = 'https://api.eol.cn/web/api/?is_single=2&local_province_id=11&page=2&province_id=&request_type=1&size=10&special_id=' + str(special_id) + '&type=&uri=apidata/api/gk/special/school&signsafe=d60d8a19b7c074516d6f7ff8caa95e4f'

    headers = {
        'user-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',  # 自定义 user-Agent
    }

    response = requests.post(special_url, headers=headers)

    if response.status_code == 200 and response.json()['code'] == '0000':
        # data = response.json()['data']['item']  # 直接提取每个页面的专业开设院校
        data = response.json()
        with open(f'special_open_school/{special_id}.json', 'w', encoding='utf-8') as special_file:
            # special_file.write(response.content)
            json.dump(data, special_file, ensure_ascii=False, indent=4)
        print(f'Downloaded page {special_id}.')
    else:
        print(f'Failed to download page {i}. Status code: {response.status_code}')

    time.sleep(5)  # 休眠5秒，防止被封IP

print('All data downloaded and merged into rank_list_merged.json.')