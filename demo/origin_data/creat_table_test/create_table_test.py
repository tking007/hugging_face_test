from sqlglot import parse_one, exp, transpile
import sqlglot


def infer_data_type(column, parsed_query):
    for binary in parsed_query.find_all(exp.Binary):
        if isinstance(binary, (exp.GT, exp.LT, exp.GTE, exp.LTE)) and column.name in {binary.left.name, binary.right.name}:
            return 'INTEGER'
    for between in parsed_query.find_all(exp.Between):
        if column.name == between.args['this'].name:
            try:
                low = between.args['low'].this
                high = between.args['high'].this
                # 检查low和high是否是字符串或数字
                if isinstance(low, (str, int, float)) and isinstance(high, (str, int, float)):
                    float(low)
                    float(high)
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
        if "SELECT" in str(table_name):
            continue
        else:
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
        if "SELECT" in str(table_name):
            continue
        else:
            if table_name not in tables:
                tables[table_name] = {('Id', 'VARCHAR')}

    if isinstance(parsed_query, exp.Select):
        for from_expr in parsed_query.find_all(exp.From):
            table_name = from_expr.this.this
            if "SELECT" in str(table_name):
                continue
            else:
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
    queries = [
    "SELECT COUNT ( * ) FROM restaurant AS t1 JOIN LOCATION AS t2 ON t1.id  =  t2.restaurant_id WHERE t2.city_name  =  \"深圳\" AND t1.name  =  \"日本料理\";"



    ]


    # s = transpile("\n".join(sentences), identity=True)
    # print(s)
    # print(sqlglot.transpile(sql[0], identify=True)[0])
    # queries = sqlglot.transpile(sql[0], identify=True)[0]
    sentences = [statement for query in queries for statement in generate_create_table(query)]
    print(sentences)

"""
请教博主给出的解决方案
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

From there you'll have the basics you need for the CREATE TABLE statement. tables, columns, 
and their datatypes. Which you can use to generate "CREATE TABLE" strings in 
regular python and pass them to SQLGlot transpile() to see if it errors. 
The SQLGlot library is huge and I'm definitely not an expert in it so there's 
probably a lot of better ways worth exploring to get datatypes of
 columns or parsing it all. My method consisted of mostly navigating 
 the syntax tree for columns and table names and then inferring datatypes 
 from the query. I then just built the CREATE statement as a regular python string, 
 but you could also use SQLGlot expressions or try using ctas 
 but I wasn't able to get that to work the way I wanted and opted for just building as a string.

Hope that helps. 
"""
