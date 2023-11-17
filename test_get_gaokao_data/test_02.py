from sqlglot import parse_one, exp

# print all column references (a and b)
for column in parse_one("SELECT AVG(Working_Horses) FROM farm WHERE Total_Horses > 5000").find_all(exp.Column):
    # for s in column.expressions:
    # print(column)
    print(column.alias_or_name)
    # print(column.this)
    # print(column.name)

# find all projections in select statements (a and c)
for select in parse_one("SELECT AVG(Working_Horses) FROM farm WHERE Total_Horses > 5000").find_all(exp.Select):
    for projection in select.expressions:
    #     print(select.operator)
    #     print(select.expressions)
    #     # if "MAX" in str(projection):
    #     #     print("sssss")
    #     # if "AVG" in str(projection):
    #     #     print("yyyyy")
    #     print(projection.this)
    #     print(projection.alias_or_name)
        if isinstance(projection, exp.Column):
            # 检查是否包含聚合函数
            if projection.function:
                # return 'INTEGER'  # 假设聚合函数的结果是整数类型
                print("--")

            # 检查是否有比较运算符
            if projection.operator in ('<', '>', '<=', '>='):
                print("--")
                # return 'INTEGER'

            # 对于聚合函数对象，也可以返回 'INTEGER' 或其他适当的数据类型
        elif isinstance(projection, exp.Avg):
            print("--")
            # return 'INTEGER'  # 假设平均值聚合函数的结果是整数类型
        #
        # return 'VARCHAR'

# find all tables (x, y, z)
# for table in parse_one("SELECT AVG(Working_Horses) FROM farm WHERE Total_Horses > 5000").find_all(exp.Table):
#     print(table)