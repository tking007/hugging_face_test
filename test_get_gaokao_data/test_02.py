# from sqlglot import parse_one, exp

# print all column references (a and b)
# for column in parse_one("SELECT DISTINCT T1.age FROM management AS T2 JOIN head AS T1 ON T1.head_id = T2.head_id WHERE T2.temporary_acting = '是'").find_all(exp.Column):
#     # for s in column.expressions:
#     # print(column)
#     print(column.alias_or_name)
# print(column.this)
# print(column.name)

# find all projections in select statements (a and c)
# for select in parse_one("SELECT DISTINCT T1.age FROM management AS T2 JOIN head AS T1 ON T1.head_id = T2.head_id WHERE T2.temporary_acting = '是'").find_all(exp.Select):
#     for projection in select.expressions:
# print(select.alias_or_name)
# print(select.expressions)
# if "MAX" in str(projection):
#     print("sssss")
# if "AVG" in str(projection):
#     print("yyyyy")
# print(exp.Predicate)
# print(projection.alias_or_name)

# find all tables (x, y, z)
# for table in parse_one("SELECT AVG(Working_Horses) FROM farm WHERE Total_Horses > 5000").find_all(exp.Table):
#     print(table)

from sqlglot import parse_one, exp, parse, transpile


single_data = \
    {
        "question": "给出有5000多匹马的农场的平均工作马的数量。",
        "answer": "SELECT avg(Working_Horses) FROM farm WHERE Total_Horses  >  5000"
    }


def demo(single_data):
    parsed_query = parse_one(single_data.get('answer'))
    # single_data.get('answer') = 'SELECT nationality FROM table_10015132_16 WHERE player = "Terrence Ross"'

    columns = []
    for table in parsed_query.find_all(exp.Table):
        for column in parsed_query.find_all(exp.Column):
            if column.table == table.alias:
                if '"' in str(column.this):
                    # sometimes things like "Terrence Ross" is thought of as a column, we ignore those
                    continue
                columns.append({'column_name': column.name})

            print(columns)
            print(table.name)

    for clause in parsed_query.find_all((exp.Avg, exp.Sum, exp.Max, exp.Min)):
        # Basically checking for numeric operations
        key = clause.this.name
        for column in columns:
            if column.get('column_name') == key:
                # Further checks to infer if type is an integer or float
                # column['type'] = inferred_type
                columns.append({'type': 'INTEGER'})


if __name__ == '__main__':
    demo(single_data)



"""
So the code I have for preparing spider isn't very clean and involved a lot of tweaking as I went to incrementally fix and catch errors within the dataset and even using sqlglot was an iterative process with maybe ten separate files that slowly came together to the final result. So nothing I can really just post and be that helpful. That being said here is some snippets of how I went about using SQLGlot. There's probably more efficient way to use it than I did though, and if anyone is a SQLGlot expert and wants to chime in, that'd be great.

If you provide the answer SQL statement to sqlglot.parse_one() you can get a syntax tree for the query

from sqlglot import parse_one, exp, parse, transpile

parsed_query = parse_one(single_data.get('answer'))
# single_data.get('answer') = 'SELECT nationality FROM table_10015132_16 WHERE player = "Terrence Ross"'

for table in parsed_query.find_all(exp.Table):
  columns = []
  for column in parsed_query.find_all(exp.Column):
    if column.table == table.alias:
      if '"' in str(column.this):
        # sometimes things like "Terrence Ross" is thought of as a column, we ignore those
        continue
      columns.append({'column_name': column.name})
  print(columns)
  print(table.name)

>>> [{'column_name': 'nationality'}, {'column_name': 'player'}]
>>> table_10015132_16
You'd also want to do something similar for datatypes of each column with something like this

for clause in parsed_query.find_all((exp.Avg, exp.Sum, exp.Max, exp.Min)):
  # Basically checking for numeric operations
  key = clause.this.name
  for column in columns:
    if column.get('column_name') == key:
      # Further checks to infer if type is an integer or float
      column['type'] = inferred_type
From there you'll have the basics you need for the CREATE TABLE statement. tables, columns, and their datatypes. Which you can use to generate "CREATE TABLE" strings in regular python and pass them to SQLGlot transpile() to see if it errors. The SQLGlot library is huge and I'm definitely not an expert in it so there's probably a lot of better ways worth exploring to get datatypes of columns or parsing it all. My method consisted of mostly navigating the syntax tree for columns and table names and then inferring datatypes from the query. I then just built the CREATE statement as a regular python string, but you could also use SQLGlot expressions or try using ctas but I wasn't able to get that to work the way I wanted and opted for just building as a string.

Hope that helps. 
"""