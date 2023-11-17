import json
import time
import re
from demo.tencent_fanyi import fanyi
import sqlglot

'''
只需要CSpider数据集中的两个字段，question和query
'''
#  这是只需要CSpider数据集中两个字段的数据
# with open("/home/susu/CSpider/train.json", "r", encoding="utf-8") as f:
#     cspider_data = json.load(f)
#
# # 提取 question 和 query 字段
# new_data = [{"question": entry["question"], "query": entry["query"]} for entry in cspider_data]
#
# # 将提取的数据写入新的 JSON 文件
# with open("test_CSpider.json", "w", encoding="utf-8") as f:
#     json.dump(new_data, f, ensure_ascii=False, indent=2)


# #  继续将answer字段中的英文\"issaquah\"翻译成中文
# with open("../demo/data_sql.json", "r", encoding="utf-8") as f:
#     datas = json.load(f)
#
# for data in datas:
#     sql_data = data["answer"]
#     match = re.search(r'\"([a-zA-Z]{3,}\s*[a-zA-Z\s]*)\"', sql_data)
#     if match:
#         answer = match.group(1)
#         if answer == "null":
#             continue
#         print(answer)
#         data["answer"] = sql_data.replace(answer, fanyi([answer])[0])
#         # data["answer"] = re.sub(re.escape(answer), fanyi([answer])[0], sql_data)
#         print(data["answer"])
#         time.sleep(1)
#
# # # 将修改后的数据写回文件
# with open("v1_data_sql.json", "w", encoding="utf-8") as f:
#     json.dump(datas, f, ensure_ascii=False, indent=2)

'''
https://huggingface.co/datasets/b-mc2/sql-create-context
https://github.com/tobymao/sqlglot#run-tests-and-lint
参照以上方法将cspider数据集转换成sql-create-context数据集格式
'''

from sqlglot import parse_one, exp


def extract_table_name(from_clause):
    if isinstance(from_clause, exp.Table):
        return from_clause.name
    elif isinstance(from_clause, exp.Join):
        # 如果是JOIN，递归调用提取子表的表名
        return extract_table_name(from_clause.right)


def infer_data_type(expression):
    if isinstance(expression, exp.Binary):
        # 如果是二元运算符，可以根据运算符类型判断数据类型
        if expression.operator in ('<', '>'):
            return 'INTEGER'
        elif isinstance(expression, exp.Aggregate):
            #  如果是聚合函数，可以根据函数类型判断数据类型
            if expression.name.lower() in ('min', 'max', 'avg', 'sum'):
                # 获取函数作用的列
                column_expression = expression.args[0]
                # 推断数据类型
                if isinstance(column_expression, exp.Column):
                    return 'INTEGER'
    # 默认为VARCHAR类型
    return 'VARCHAR'


def generate_create_table(query):
    # 使用SQLGlot解析SQL查询
    parsed_query = parse_one(query)

    # 提取表名和列信息
    table_name = None
    columns = []

    # 提取表名
    for from_clause in parsed_query.find_all(exp.Table):
        table_name = extract_table_name(from_clause)
        print(table_name)
        if table_name:
            break

    # 提取列信息
    for select_clause in parsed_query.find_all(exp.Column):
        # print("****", select_clause.alias_or_name)
        col_name = select_clause.alias_or_name
        print(col_name)
        expression = select_clause.expression
        data_type = infer_data_type(expression)
        columns.append((select_clause.alias_or_name, data_type))
        # columns.append((select_clause.alias_or_name, 'VARCHAR'))  # 默认为VARCHAR类型

    # 生成CREATE TABLE语句
    create_table_statement = f"CREATE TABLE {table_name} ({', '.join([f'{col} {data_type}' for col, data_type in columns])});"

    # 再次使用 SQLGlot 来确保 SQL 查询和 CREATE TABLE 语句解析没有错误
    try:
        parse_one(create_table_statement)
    except Exception as e:
        print(f"Error parsing CREATE TABLE statement: {e}")

    return create_table_statement


with open("test_CSpider.json", "r", encoding="utf-8") as f:
    datas = json.load(f)

# 处理数据集
for entry in datas[:10]:
    entry["context"] = generate_create_table(entry["query"])

# 打印处理后的数据集
for entry in datas[:10]:
    print(entry["context"])
    print(entry)
