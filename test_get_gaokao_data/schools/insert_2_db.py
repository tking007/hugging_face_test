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


"""
admissions: 可能是关于学校的招生信息。
answerurl: 招生办网址(官方招生咨询平台)。
belong: 学校可能属于哪个组织或机构。
central: 可能表示学校是否属于中央直辖。
city_id 和 city_name: 学校所在城市的ID和名称。
code_enroll: 可能是学校的招生代码。
colleges_level: 可能是学校的等级或级别。
county_id 和 county_name: 学校所在县的ID和名称。
department: 可能是学校的部门或学院。
doublehigh: 可能表示学校是否是双一流高校。
dual_class 和 dual_class_name: 可能表示学校是否是双一流学科，以及双一流学科的名称。
f211 和 f985: 可能表示学校是否是211工程或985工程的高校。
hightitle: 可能是学校的高级标题或名称。
inner_rate: 可能是学校的内部评级或排名。
is_recruitment: 可能表示学校是否正在招生。
level 和 level_name: 学校的级别或等级，以及级别或等级的名称。
name: 学校的名称。
school_image: 学校的图片。
nature 和 nature_name: 学校的性质（如公立或私立），以及性质的名称。
outer_rate: 可能是学校的外部评级或排名。
province_id 和 province_name: 学校所在省份的ID和名称。
rank 和 rank_type: 学校的排名，以及排名的类型。
rate: 可能是学校的评级或评分。
school_id: 学校的ID。
school_type: 学校的类型（如大学或高中）。
tag_name: 可能是学校的标签或关键词。
type 和 type_name: 学校的类型，以及类型的名称。
view_month, view_total, view_total_number, view_week: 可能是关于学校的浏览量或访问量的信息。
short: 可能是学校的简称。
old_name: 学校的旧名称。
proid: 可能是学校的产品ID或项目ID。
school_website: 学校的网站URL。
"""