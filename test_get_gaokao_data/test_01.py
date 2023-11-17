from sqlglot import exp, parse_one
import json


def extract_table_name(from_clause):
    if isinstance(from_clause, exp.Table):
        return from_clause.name
    elif isinstance(from_clause, exp.Join):
        return extract_table_name(from_clause.right)


def infer_data_type(projection, query):
    if '<=' in query:
        return 'INTEGER'
    elif '>=' in query:
        return 'INTEGER'
    elif '<' in query:
        return 'INTEGER'
    elif '>' in query:
        return 'INTEGER'

    if 'min' in str(projection) or "MIN" in str(projection):
        return 'INTEGER'
    elif 'max' in str(projection) or "MAX" in str(projection):
        return 'INTEGER'
    elif 'avg' in str(projection):
        return 'INTEGER'
    elif 'sum' in str(projection):
        return 'INTEGER'
    # 如果是数字类型的字面值，返回整数类型
    # if any(char.isdigit() for char in expression):
    #     return 'INTEGER'
    # 默认为VARCHAR类型
    return 'VARCHAR'


def generate_create_table(query):
    try:
        parsed_query = parse_one(query)
        table_name = None
        columns = []

        for from_clause in parsed_query.find_all(exp.Table):
            table_name = extract_table_name(from_clause)

        for select_clause in parsed_query.find_all(exp.Select):
            for projection in select_clause.expressions:
                data_type = infer_data_type(projection, query)
        for column in parsed_query.find_all(exp.Column):
            col_name = column.alias_or_name
            columns.append((column.this, data_type))

        create_table_statement = f"CREATE TABLE {table_name} ("

        added_columns = set()
        for column_name, data_type in columns:
            if column_name in added_columns:
                continue
            create_table_statement += f"{column_name} {data_type},"
            added_columns.add(column_name)

        if not columns:
            create_table_statement += "Id INTEGER,\n"

        create_table_statement = create_table_statement.rstrip(',') + ");"

        # 再次使用 SQLGlot 来确保 SQL 查询和 CREATE TABLE 语句解析没有错误
        try:
            parse_one(create_table_statement)
        except Exception as e:
            print(f"Error parsing CREATE TABLE statement: {e}")

        return create_table_statement

    except Exception as e:
        print(f"Error parsing query: {query}")
        print(f"Error message: {str(e)}")

    return None


# # 示例 SQL 查询
# with open('test_CSpider.json', 'r', encoding='utf-8') as f:
#     datas = json.load(f)
#
#
# # 处理数据集
# for entry in datas[:10]:
#     entry["context"] = generate_create_table(entry["query"])
#     entry['answer'] = entry.pop('query')
#
# # 打印处理后的数据集
# for entry in datas[:10]:
#     print(entry["context"])
#     # print(entry)

datas = "SELECT Status FROM city WHERE Population > 1500 INTERSECT SELECT Status FROM city WHERE Population < 500"
print(generate_create_table(datas))