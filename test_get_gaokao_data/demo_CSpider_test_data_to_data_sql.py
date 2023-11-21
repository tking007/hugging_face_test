import json
import time
import re
from demo.tencent_fanyi import fanyi
from sqlglot import parse_one, exp, transpile

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

"""
https://huggingface.co/datasets/b-mc2/sql-create-context

https://github.com/tobymao/sqlglot#run-tests-and-lint
参照以上方法将cspider数据集转换成sql-create-context数据集格式
"""

from sqlglot import parse_one, exp, transpile


def infer_data_type(column, parsed_query):
    for binary in parsed_query.find_all(exp.Binary):
        if isinstance(binary, (exp.GT, exp.LT, exp.GTE, exp.LTE)) and column.name in {binary.left.name,
                                                                                      binary.right.name}:
            return 'INTEGER'
    for between in parsed_query.find_all(exp.Between):
        if column.name == between.args['this'].name:
            try:
                float(between.args['low'].this)
                float(between.args['high'].this)
                return 'INTEGER'
            except ValueError:
                pass
    for aggregate in parsed_query.find_all((exp.Avg, exp.Sum, exp.Max, exp.Min)):
        if column.name == aggregate.this.name:
            return 'INTEGER'
    return 'VARCHAR'


def generate_create_table(query_or_expr):
    parsed_query = parse_one(query_or_expr) if isinstance(query_or_expr, str) else query_or_expr
    tables = {}

    for table_expr in parsed_query.find_all((exp.From, exp.Join)):
        table_name = table_expr.this.this
        tables[table_name] = set()

        for column in parsed_query.find_all(exp.Column):
            if column.table == table_expr.this.alias and '"' not in str(column.this):
                column_name = column.name
                data_type = infer_data_type(column, parsed_query)
                tables[table_name].add((column_name, data_type))

    for union in parsed_query.find_all(exp.Union):
        generate_create_table(union.left)
        generate_create_table(union.right)

    for from_expr in parsed_query.find_all(exp.From):
        table_name = from_expr.this.this
        if table_name not in tables:
            tables[table_name] = {('Id', 'VARCHAR')}

    if isinstance(parsed_query, exp.Select):
        for from_expr in parsed_query.find_all(exp.From):
            table_name = from_expr.this.this
            if table_name not in tables:
                tables[table_name] = {('Id', 'VARCHAR')}

    create_table_statements = []
    for table_name, columns_info in tables.items():
        columns_info = columns_info or {('Id', 'VARCHAR')}
        create_table_statement = f"CREATE TABLE {table_name} ("
        create_table_statement += ', '.join(f"{column_info[0]} {column_info[1]}" for column_info in columns_info)
        create_table_statement += ");"
        create_table_statements.append(create_table_statement)

    return create_table_statements


if __name__ == '__main__':
    with open("test_CSpider.json", "r", encoding="utf-8") as f:
        datas = json.load(f)

    sentences = []

    # 处理数据集
    for entry in datas[:10]:
        entry["context"] = generate_create_table(entry["query"])

        if entry["context"]:
            for statement in entry["context"]:
                sentences.append(statement)
        else:
            print("未生成 create table 语句。")

    print(sentences)
    s = transpile("\n".join(sentences), identity=True)
    print(s)
