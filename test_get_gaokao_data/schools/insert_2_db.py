import sqlite3
import json
import os

# 读取 JSON 数据
with open('school_detail.json', 'r', encoding='utf-8') as json_file:
    data_detail = json.load(json_file)

with open('school_name.json', 'r', encoding='utf-8') as json_file:
    data_name = json.load(json_file)

# 连接到 SQLite 数据库
conn = sqlite3.connect('../test.sqlite')
cursor = conn.cursor()

# 创建数据库表（如果不存在）
cursor.execute('''
    CREATE TABLE IF NOT EXISTS schools (
        admissions TEXT,
        answerurl TEXT,
        belong TEXT,
        central TEXT,
        city_id TEXT,
        city_name TEXT,
        code_enroll TEXT,
        colleges_level TEXT,
        county_id TEXT,
        county_name TEXT,
        department TEXT,
        doublehigh TEXT,
        dual_class TEXT,
        dual_class_name TEXT,
        f211 TEXT,
        f985 TEXT,
        hightitle TEXT,
        inner_rate TEXT,
        is_recruitment TEXT,
        level TEXT,
        level_name TEXT,
        name TEXT,
        school_image BLOB,
        nature TEXT,
        nature_name TEXT,
        outer_rate TEXT,
        province_id TEXT,
        province_name TEXT,
        rank TEXT,
        rank_type TEXT,
        rate TEXT,
        school_id TEXT PRIMARY KEY,
        school_type TEXT,
        tag_name TEXT,
        type TEXT,
        type_name TEXT,
        view_month TEXT,
        view_total TEXT,
        view_total_number TEXT,
        view_week TEXT,
        short TEXT,
        old_name TEXT,
        proid TEXT,
        school_website TEXT
    )
''')

# 指定本地存储图片的主目录
main_image_dir = 'school_images'

# 插入数据到数据库
for school_detail in data_detail['data']:
    school_id = school_detail.get('school_id')
    image_path = os.path.join(main_image_dir, str(school_id), f'{school_id}.jpg')

    # 读取图像文件的二进制数据
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()

    # 为新字段website提供值
    website = f'https://www.gaokao.cn/school/{school_id}'
    school_detail['school_image'] = image_data
    school_detail['school_website'] = website  # 新字段的值

    placeholders = ', '.join(['?'] * len(school_detail))
    columns = ', '.join(school_detail.keys())
    values = list(school_detail.values())

    sql = f'INSERT INTO schools ({columns}) VALUES ({placeholders})'

    cursor.execute(sql, values)

# 提交更改并关闭数据库连接
conn.commit()
conn.close()
