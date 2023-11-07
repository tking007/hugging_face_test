# jpg_url = 'https://static-data.gaokao.cn/upload/logo/3651.jpg'  # 3651是school_id

import json

'''
爬取学校图片
'''

# 从学校数据文件加载学校信息
with open('school_detail.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 指定本地存储图片的主目录
main_image_dir = 'school_images'

# 创建存储图片的主目录（如果不存在）
os.makedirs(main_image_dir, exist_ok=True)

for school in data['data']:
    school_id = school.get('school_id')
    school_image_url = 'https://static-data.gaokao.cn/upload/logo/' + str(school_id) + '.jpg'

    # 下载图片并保存到独立的子目录
    school_image_dir = os.path.join(main_image_dir, str(school_id))
    os.makedirs(school_image_dir, exist_ok=True)

    response = requests.get(school_image_url)
    if response.status_code == 200 and response.json()['code'] == '0000':
        image_filename = os.path.join(school_image_dir, f'{school_id}.jpg')
        with open(image_filename, 'wb') as image_file:
            image_file.write(response.content)

# # 存储已下载图片的子目录路径到学校数据中
# for school in data['data']:
#     school_id = school.get('school_id')
#     school[';'] = os.path.join(main_image_dir, str(school_id))
#
# # 更新带有子目录路径的数据文件
# with open('school_detail.json', 'w', encoding='utf-8') as file:
#     json.dump(data, file, ensure_ascii=False, indent=4)