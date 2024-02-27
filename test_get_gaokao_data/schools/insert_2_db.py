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
admissions: 是否是强基计划。
answerurl: 招生办网址(官方招生咨询平台)。
belong: 学校可能属于哪个部门。
central: 表示学校是否属于中央部委。
city_id: 学校所在城市的ID. 
city_name: 学校所在城市的名称。
code_enroll: 学校的招生代码。
colleges_level: 表示院校级别，有省级示范、国家级骨干等。
county_id: 学校所在区县的ID。
county_name: 学校所在区县的名称。
department: 是否教育部直属。
doublehigh: 是否是双高计划。
dual_class: 38000(一流学科建设高校)38001(一流大学建设高校A类) 38002(一流大学建设高校B类)。
dual_class_name: 双一流学科的名称。
f211: 是否是211工程高校。
f985: 是否985工程的高校。
hightitle: 学校名称。
inner_rate: 内部排名。
is_recruitment: 表示学校是否正在招生。
level: 教育等级, "普通本科":2001, "专科（高职）": 2002。
level_name: 教育等级名称。
name: 学校的名称。
school_image: 学校的图片。
nature: 办学类型，36000: "公办", 36001: "民办"。
nature_name: 办学类型名称。
outer_rate: 外部排名。
province_id: 学校所在省份的ID。
province_name: 学校所在省份的I名称。
rank: 学校的排名。
rank_type: 学校的排名类型。
rate: 学校的评分。
school_id: 学校的ID。
school_type: 办学类型："普通本科": "6000","专科（高职)": , 6002: "独立学院", 6003: "中外合作办学", 6007: "其他"。
tag_name: 学校的标签或关键词。
type: 学校的类型。
type_name: 学校的类型，以及类型的名称。
view_month: 学校的月浏览量。
view_total: 学校的总浏览量缩略形式。
view_total_number: 学校的总浏览量数字形式。
view_week: 学校周浏览量。
short: 学校的简称。
old_name: 学校的旧名称。
proid: 学校的项目ID。
school_website: 学校的网站URL。
"""