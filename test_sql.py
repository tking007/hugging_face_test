from sqlglot import parse_one, exp

# print all column references (a and b)
# for column in parse_one("select T2.名称 , T2.类型 from 学校毕业人数 as T1 join 学校 as T2 on 学校毕业人数.学校id == 学校.词条id where T1.2016届人数 <= 4000 order by T1.2014届人数 asc").find_all(exp.Column):
#     print(column.alias_or_name)

# find all projections in select statements (a and c)
# for select in parse_one("select T2.name , T2.type from school_graduates as T1 join school as T2 on school_graduates.school_id = school.entry_id where T1.2016_graduates <= 4000 order by T1.2014_graduates asc").find_all(exp.Select):
#     for projection in select.expressions:
#         print(projection.alias_or_name)

# find all tables (x, y, z)
# for table in parse_one("select T2.名称 , T2.类型 from 学校毕业人数 as T1 join 学校 as T2 on 学校毕业人数.学校id == 学校.词条id where T1.2016届人数 <= 4000 order by T1.2014届人数 asc").find_all(exp.Table):
#     print(table.name)

import sqlglot

sql ="( select 城市 from 城市 where 城市面积 < 17000 ) union ( select 城市 from 城市 order by 通勤高峰实际速度(千米/时) desc limit 3 )"


# print(sqlglot.transpile(sql, identify=True)[0])

import re
import json
#
# def preprocess_query(query):
#     # 创建一个映射表，将阿拉伯数字映射为中文数字
#     num_map = {'0': '零', '1': '一', '2': '二', '3': '三', '4': '四', '5': '五', '6': '六', '7': '七', '8': '八', '9': '九'}
#     # 匹配数字和中文字符的混合部分
#     pattern = re.compile(r'(\d+)([\u4e00-\u9fa5]+)')
#     # 使用中文字符和映射表替换匹配到的部分
#     processed_query = re.sub(pattern, lambda m: ''.join(num_map[i] for i in m.group(1)) + m.group(2), query)
#     return processed_query
#
# print(sql)
# print(preprocess_query(sql))

def preprocess_query(query, pattern):
    # 创建一个映射表，将阿拉伯数字映射为中文数字
    num_map = {'0': '零', '1': '一', '2': '二', '3': '三', '4': '四', '5': '五', '6': '六', '7': '七', '8': '八', '9': '九'}
    # 匹配数字和中文字符的混合部分
    pattern = re.compile(r'(\d+)([\u4e00-\u9fa5]+)')
    # 使用中文字符和映射表替换匹配到的部分
    processed_query = re.sub(pattern, lambda m: ''.join(num_map[i] for i in m.group(1)) + m.group(2), query)
    return processed_query



# 匹配不被引号包裹的数字和中文字符混合的部分
pattern = re.compile(r'(?<=\s)(\d+)([\u4e00-\u9fa5]+)(?=\s|$)')

with open("./demo/origin_data/DUSQL/train.json", "r", encoding="utf-8") as f:
    data = json.load(f)

    for entry in data:
        query = entry['query']
        # 使用正则表达式模式匹配query
        if pattern.search(query):
            print(query)
            # 使用中文字符和映射表替换匹配到的部分
            processed_query = preprocess_query(query, pattern)
            print("---", processed_query)
            print("***", sqlglot.transpile(processed_query, identify=True)[0])
