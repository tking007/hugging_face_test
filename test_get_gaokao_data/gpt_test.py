from sqlglot import parse_one, exp, transpile


def infer_data_type(column, parsed_query):
    # 检查列是否在比较操作中使用
    for binary in parsed_query.find_all(exp.Binary):
        if isinstance(binary, (exp.GT, exp.LT, exp.GTE, exp.LTE)) and (
                column.name == binary.left.name or column.name == binary.right.name):
            return 'INTEGER'
    # 检查列是否在 BETWEEN 操作中使用
    for between in parsed_query.find_all(exp.Between):
        if column.name == between.args['this'].name:
            try:
                float(between.args['low'].this)
                float(between.args['high'].this)
                return 'INTEGER'
            except ValueError:
                pass
    # 检查列是否在聚合函数中使用
    for aggregate in parsed_query.find_all((exp.Avg, exp.Sum, exp.Max, exp.Min)):
        if column.name == aggregate.this.name:
            return 'INTEGER'
    # 如果没有找到数值操作，则默认为 VARCHAR
    return 'VARCHAR'


def generate_create_table(query_or_expr):
    try:
        if isinstance(query_or_expr, str):
            parsed_query = parse_one(query_or_expr)
        else:
            parsed_query = query_or_expr

        tables = {}

        for table_expr in parsed_query.find_all((exp.From, exp.Join)):
            table_name = table_expr.this.this
            tables[table_name] = []

            for column in parsed_query.find_all(exp.Column):
                if column.table == table_expr.this.alias and '"' not in str(column.this):
                    column_name = column.name
                    data_type = infer_data_type(column, parsed_query)
                    if (column_name, data_type) not in tables[table_name]:
                        tables[table_name].append((column_name, data_type))

        for union in parsed_query.find_all(exp.Union):
            generate_create_table(union.left)
            generate_create_table(union.right)

        for from_expr in parsed_query.find_all(exp.From):
            table_name = from_expr.this.this
            if table_name not in tables:
                tables[table_name] = [('Id', 'VARCHAR')]

        if isinstance(parsed_query, exp.Select):
            for from_expr in parsed_query.find_all(exp.From):
                table_name = from_expr.this.this
                if table_name not in tables:
                    tables[table_name] = [('Id', 'VARCHAR')]

        create_table_statements = []
        for table_name, columns_info in tables.items():
            if not columns_info:
                columns_info = [('Id', 'VARCHAR')]  # Add a default column if no columns were found

            create_table_statement = f"CREATE TABLE {table_name} ("
            for column_info in columns_info:
                create_table_statement += f"{column_info[0]} {column_info[1]}, "
            create_table_statement = create_table_statement.rstrip(', ') + ");"
            create_table_statements.append(create_table_statement)

        return create_table_statements

    except Exception as e:
        print(f"解析查询时出错: {query_or_expr}")
        print(f"错误信息: {str(e)}")

    return None


if __name__ == '__main__':
    queries = [
        "SELECT T1.name, T1.id FROM station AS T1 JOIN status AS T2 ON T1.id = T2.station_id GROUP BY T2.station_id HAVING AVG(T2.bikes_available) > 14 UNION SELECT name, id FROM station WHERE installation_date LIKE \"十二月\""


        ]
    sentences = []
    for query in queries:
        create_table_statements = generate_create_table(query)
        if create_table_statements:
            for statement in create_table_statements:
                sentences.append(statement)
        else:
            print("未生成 create table 语句。")

    print(sentences)
    s = transpile("\n".join(sentences), identity=True)
    print(s)
