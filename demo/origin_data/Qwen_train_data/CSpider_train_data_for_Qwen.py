import json
import sqlite3


def get_db_schemas(all_db_infos):
    db_schemas = {}

    for db in all_db_infos:
        table_names_original = db["table_names_original"]
        table_names = db["table_names"]
        column_names_original = db["column_names_original"]
        column_names = db["column_names"]
        column_types = db["column_types"]

        db_schemas[db["db_id"]] = {}

        primary_keys, foreign_keys = [], []
        # record primary keys
        for pk_column_idx in db["primary_keys"]:
            pk_table_name_original = table_names_original[column_names_original[pk_column_idx][0]]
            pk_column_name_original = column_names_original[pk_column_idx][1]

            primary_keys.append(
                {
                    "table_name_original": pk_table_name_original.lower(),
                    "column_name_original": pk_column_name_original.lower()
                }
            )

        db_schemas[db["db_id"]]["pk"] = primary_keys

        # record foreign keys
        for source_column_idx, target_column_idx in db["foreign_keys"]:
            fk_source_table_name_original = table_names_original[column_names_original[source_column_idx][0]]
            fk_source_column_name_original = column_names_original[source_column_idx][1]

            fk_target_table_name_original = table_names_original[column_names_original[target_column_idx][0]]
            fk_target_column_name_original = column_names_original[target_column_idx][1]

            foreign_keys.append(
                {
                    "source_table_name_original": fk_source_table_name_original.lower(),
                    "source_column_name_original": fk_source_column_name_original.lower(),
                    "target_table_name_original": fk_target_table_name_original.lower(),
                    "target_column_name_original": fk_target_column_name_original.lower(),
                }
            )
        db_schemas[db["db_id"]]["fk"] = foreign_keys

        db_schemas[db["db_id"]]["schema_items"] = []
        for idx, table_name_original in enumerate(table_names_original):
            column_names_original_list = []
            column_names_list = []
            column_types_list = []

            for column_idx, (table_idx, column_name_original) in enumerate(column_names_original):
                if idx == table_idx:
                    column_names_original_list.append(column_name_original.lower())
                    column_names_list.append(column_names[column_idx][1].lower())
                    column_types_list.append(column_types[column_idx])

            db_schemas[db["db_id"]]["schema_items"].append({
                "table_name_original": table_name_original.lower(),
                "table_name": table_names[idx].lower(),
                "column_names": column_names_list,
                "column_names_original": column_names_original_list,
                "column_types": column_types_list
            })

    return db_schemas


def get_schema(db):
    """
    Get database's schema, which is a dict with table name as key
    and list of column names as value
    :param db: database path
    :return: schema dict
    """

    schema = {}
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [str(table[0].lower()) for table in cursor.fetchall()]

    for table in tables:
        cursor.execute("PRAGMA table_info({})".format(table))
        columns = [str(col[1].lower()) for col in cursor.fetchall()]
        schema[table] = {}

        for column in columns:
            # print(f"Table: {table}, Column: {column}")  # Print table schema
            try:
                cursor.execute(f"SELECT DISTINCT `{column}` FROM `{table}`")
                values = [row[0] for row in cursor.fetchall()]
                schema[table][column] = values
            except sqlite3.OperationalError as e:
                print(f"Error: {e}")
                continue

    return schema


# def get_column_values(db_path, table_name, column_name):
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#
#     cursor.execute(f"SELECT DISTINCT {column_name} FROM {table_name}")
#     values = [row[0] for row in cursor.fetchall()]
#
#     conn.close()
#
#     return values


def convert_to_training_data(input_data, instruction, output_format):
    db_path = "/home/susu/CSpider/database"
    all_db_infos = json.load(open("../CSpider/tables.json", "r", encoding="utf-8"))

    training_data = []
    db_schemas = get_db_schemas(all_db_infos)
    for item in input_data:
        db_id = item['db_id']
        schema = get_schema(db_path + "/{}/{}.sqlite".format(db_id, db_id))
        schema_info = ""
        for table in db_schemas[db_id]["schema_items"]:
            table_name_original = table["table_name_original"]
            table_name = table["table_name"]
            column_names = table["column_names"]
            column_names_original = table["column_names_original"]
            column_types = table["column_types"]

            schema_column = ""
            for column_name_original, column_name, column_type in zip(column_names_original, column_names, column_types):
                # print("@@", column_name_original, table_name_original, db_id)
                possible_values = schema[table_name_original][column_name_original]
                schema_column += f"The {column_name_original} field of {table_name} means {column_name} and has possible values as: {possible_values}.\n"

            schema_info += f"""
            CREATE TABLE {table_name_original} ({', '.join([f'{name} {type_1}' for name, type_1 in zip(column_names_original, column_types)])});
            /*The table {table_name_original} description is: '{table_name}'.
            {schema_column}
            */
            """

        conversation = f"""
        "Question":  {item['question']}
        "SQLQuery": {item['query']}
        """

        training_item = {
            "instructions": instruction,
            "output_format": output_format,
            "context": schema_info,
            "conversations": conversation
        }
        training_data.append(training_item)

    return training_data


if __name__ == '__main__':
    with open("/home/susu/下载/CSpider/train.json", "r", encoding="utf-8") as f:
        origin_data = json.load(f)

    instruction = """
    You are a MySQL expert. Given an input question, first create a syntactically correct SQL
    query to run, then look at the results of the query and return the answer to the input question.
    You must query only the columns that are needed to answer the question.
    Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist.
    pay attention to which columns is in which table.
    Pay attention to that the constraint variables are case sensitive and must match the columns name.
    Pay attention to return an executable sql query.
    Pay attention to that the values of variables need to be enclosed in quotation marks, for example: it should be ' SELECT col_1 FROM Table_69d3e454334311e9831e542696d6e445
    WHERE col_7 < abc ' instead of 'SELECT col_1 FROM Table_69d3e454334311e9831e542696d6e445 WHERE col_7 < "abc"'.
    Pay attention to that SQL tables need to be given aliases when using join, for example: it should be 'SELECT a.name FROM actor AS a JOIN cast AS c ON a.aid = c.aid JOIN
    movie AS m ON c.msid = m.mid WHERE m.title = '霸王别姬" AND c.role = '程蝶衣'' instead of 'SELECT actor.name FROM actor JOIN cast ON actor.aid = cast.aid JOIN
    movie ON cast.msid = movie.mid WHERE movie.title = '霸王别姬' AND cast.role = '程蝶衣''.

    Output the final SQL query only.
    """

    output_format = """
    Use the following format:
    SQLQuery:  SQL Query here.
    Only use the following tables:
    """

    # Convert to training data
    training_data = convert_to_training_data(origin_data, instruction, output_format)

    # Write the training data to a new JSON file
    with open("CSpider_for_Qwen_v2.json", "w", encoding="utf-8") as f:
        json.dump(training_data, f, ensure_ascii=False, indent=2)
        print("Done!")
