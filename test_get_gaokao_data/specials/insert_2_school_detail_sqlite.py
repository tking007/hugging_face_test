# import sqlite3
# import json
#
# # 连接到数据库（如果不存在，则创建）
# conn = sqlite3.connect('test_get_gaokao_data/schools/test.sqlite')
# cursor = conn.cursor()
#
# # 创建专业信息表
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS major_info (
#         major_id TEXT PRIMARY KEY,
#         major_name TEXT,
#         degree TEXT,
#         limit_year TEXT,
#         rank INTEGER,
#         salaryavg REAL
#     )
# ''')
#
# # 创建专业分类表
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS major_category (
#         category_id TEXT PRIMARY KEY,
#         category_name TEXT
#     )
# ''')
#
# # 创建开设院校信息表
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS school_info (
#         school_id TEXT PRIMARY KEY,
#         school_name TEXT,
#         city_name TEXT,
#         department TEXT,
#         nature_name TEXT,
#         level_name TEXT,
#         ruanke_level TEXT,
#         ruanke_rank TEXT,
#         tag_name TEXT,
#         type_name TEXT
#     )
# ''')
#
# # 读取专业信息的 JSON 数据
# with open('specials_lists.json', 'r', encoding='utf-8') as major_file:
#     major_data = json.load(major_file)
#
# # 读取专业分类的 JSON 数据
# with open('special_info.json', 'r', encoding='utf-8') as category_file:
#     category_data = json.load(category_file)
#
#
# school_main_path = 'special_open_school'
#
# for major in major_data['data']:
#     special_id = major.get('special_id')
#     school_info_path = os.path.join(school_main_path, str(special_id), f'{special_id}.json')
#
#     # 读取开设院校信息的 JSON 数据
#     with open(school_info_path, 'r', encoding='utf-8') as special_file:
#         special_data = json.load(special_file)
#
#
# # 连接到数据库
# conn = sqlite3.connect('gaokao_data.sqlite')
# cursor = conn.cursor()
#
# # 插入专业信息
# for major in major_data['data']:
#     cursor.execute('''
#         INSERT INTO major_info (major_id, major_name, degree, limit_year, rank, salaryavg)
#         VALUES (?, ?, ?, ?, ?, ?)
#     ''', (
#         major['id'], major['name'], major['degree'], major['limit_year'],
#         major['rank'], major['salaryavg']
#     ))
#
# # 插入专业分类
# for category_id, category_items in category_data.items():
#     for item in category_items['item']:
#         cursor.execute('''
#             INSERT INTO major_category (category_id, category_name)
#             VALUES (?, ?)
#         ''', (item['code'], item['name']))
#
# # 插入开设院校信息
# for school in special_data['data']:
#     cursor.execute('''
#         INSERT INTO school_info (school_id, school_name, city_name, department, nature_name, level_name, ruanke_level, ruanke_rank, tag_name, type_name)
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     ''', (
#         school['school_id'], school['name'], school['city_name'], school['department'],
#         school['nature_name'], school['level_name'], school['ruanke_level'],
#         school['ruanke_rank'], school['tag_name'], school['type_name']
#     ))
#
# # 提交更改并关闭数据库连接
# conn.commit()
# conn.close()


import sqlite3
import json
import os

# 连接到数据库（如果不存在，则创建）
conn = sqlite3.connect('../schools/school_detail.sqlite')
cursor = conn.cursor()

# 创建专业分类表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS major_categories (
        special_id TEXT PRIMARY KEY,
        name TEXT,
        code TEXT
    )
''')

# 创建专业表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS majors (
        major_id TEXT PRIMARY KEY,
        major_name TEXT,
        degree TEXT,
        limit_year TEXT,
        rank INTEGER,
        salaryavg REAL,
        category_id TEXT,
        FOREIGN KEY (category_id) REFERENCES major_categories (category_id)
    )
''')

# 创建学校表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS schools (
        school_id TEXT PRIMARY KEY,
        school_name TEXT,
        city_name TEXT,
        department TEXT,
        nature_name TEXT,
        level_name TEXT,
        ruanke_level TEXT,
        ruanke_rank TEXT,
        tag_name TEXT,
        type_name TEXT
    )
''')

# 创建专业和学校的关联表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS major_school (
        major_id TEXT,
        school_id TEXT,
        PRIMARY KEY (major_id, school_id),
        FOREIGN KEY (major_id) REFERENCES majors (major_id),
        FOREIGN KEY (school_id) REFERENCES schools (school_id)
    )
''')

# 读取专业信息的 JSON 数据
with open('specials_lists.json', 'r', encoding='utf-8') as major_file:
    major_data = json.load(major_file)

# 读取专业分类的 JSON 数据
with open('special_info.json', 'r', encoding='utf-8') as category_file:
    category_data = json.load(category_file)

school_main_path = 'special_open_school'

# 插入专业分类
for category_id, category_items in category_data['data'].items():
    for item in category_items['item']:
        cursor.execute('''
            INSERT INTO major_categories (special_id, name, code)
            VALUES (?, ?,?)
        ''', (item['spe_id'], item['name'], item['code']))

# 插入专业信息
for major in major_data['data']:
    cursor.execute('''
        INSERT INTO majors (major_id, major_name, degree, limit_year, rank, salaryavg, category_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        major['id'], major['name'], major['degree'], major['limit_year'],
        major['rank'], major['salaryavg'], major['special_id']
    ))

    special_id = major.get('special_id')
    school_info_path = os.path.join(school_main_path, f'{special_id}.json')

    # 读取开设院校信息的 JSON 数据
    with open(school_info_path, 'r', encoding='utf-8') as special_file:
        special_data = json.load(special_file)

    # 插入开设院校信息
    for school in special_data['data']['item']:
        cursor.execute('''
            SELECT school_id FROM schools WHERE school_id = ?
        ''', (school['school_id'],))
        result = cursor.fetchone()
        if result is None:
            cursor.execute('''
                INSERT INTO schools (school_id, school_name, city_name, department, nature_name, level_name, ruanke_level, ruanke_rank, tag_name, type_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                school['school_id'], school['name'], school['city_name'], school['department'],
                school['nature_name'], school['level_name'], school['ruanke_level'],
                school['ruanke_rank'], school['tag_name'], school['type_name']
            ))

        # 插入专业和学校的关联信息
        cursor.execute('''
            INSERT INTO major_school (major_id, school_id)
            VALUES (?, ?)
        ''', (major['id'], school['school_id']))

# 提交更改并关闭数据库连接
conn.commit()
conn.close()
