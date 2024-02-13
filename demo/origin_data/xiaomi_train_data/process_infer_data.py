import json
from process_train_data_for_Qwen import mean_pooling, encoder_decoder_1, model, tokenizer
import sqlite3
import os

def process_infer_data(infer_origin_data, instruction):
    prompts = []
    for line_dict in infer_origin_data:
        question = line_dict["question"]
        db_id = line_dict["db_id"]

        schema_info = f""

        # Connect to database and fetch table names and column names
        conn = sqlite3.connect(f'../../../test_get_gaokao_data/schools/{db_id}.sqlite')
        # conn = sqlite3.connect('actor_database.db')
        cursor = conn.cursor()

        # Get the filename that is connected above
        filename = conn.cursor().execute("PRAGMA database_list;").fetchall()[0][2]

        # Extract file name from file path
        database_name = os.path.basename(filename).split('.')[0]

        table_names = [table_info[0] for table_info in cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table';").fetchall()]

        # print(table_names)

        column_names = []
        for table_name in table_names:
            cursor.execute(f"PRAGMA table_info(`{table_name}`);")
            table_column_names = [column_info[1] for column_info in cursor.fetchall()]
            # 处理列名中的下划线，替换为空格
            # table_column_names = [column_name.replace("_", " ") for column_name in table_column_names]
            column_names.extend(table_column_names)

            # print(table_column_names)
        # print(column_names)

        # highest_matching_table_name, highest_matching_table_column_names = encoder_decoder_1(
        #     question, table_names, tokenizer, model, cursor)

        schema_column = ""

        for column_name in column_names:
            # print(column_name_original, table_name_original, column_type)
            cursor.execute(f"SELECT  DISTINCT `{column_name}` FROM `{table_names[0]}` LIMIT 100")
            # print(column_name_original, table_name_original, db_id)
            possible_values = [str(row[0]) for row in cursor.fetchall()]
            # print(possible_values)

            if len(possible_values) == 0 or possible_values == ['']:
                highest_matching_column_info = ''
            else:
                # print("sss", possible_values)
                highest_matching_column_info = encoder_decoder_1(question, possible_values, tokenizer, model, cursor)[:5]
                # print("@@@", highest_matching_column_info)

            column_name_original = column_name.replace("_", " ")
            schema_column += f"The {column_name} field of {table_names[0]} means {column_name_original} and has possible values as: {highest_matching_column_info}.\n"

        schema_info = f"""
        {schema_column}
        */"""

        conversation = f"""
        "Question": {question}
        "SQLQuery": 
        """

        prompt = f"{instruction} {schema_info} {conversation}"

        prompts.append(prompt)
        conn.close()

    return prompts






if __name__ == '__main__':
    infer_origin_data = []
    with open("infer.txt", "r", encoding='utf-8') as f:
        for line in f:
            infer_origin_data.append(json.loads(line))
        # for line in f:
        #     line_dict = json.loads(line)
        #     question = line_dict["question"]
        #     db_id = line_dict["db_id"]

    instruction = """You are a MySQL expert. Given an input question, first create a syntactically correct SQL
    Query to run, then look at the results of the query and return the answer to the input question.
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
    
    Use the following format:
    SQLQuery:  SQL Query here.
    Only use the following tables:
    
    CREATE TABLE "school_detail" ("admissions" TEXT, "answerurl" TEXT, "belong" TEXT, "central" TEXT, "city_id" TEXT, "city_name" TEXT, "code_enroll" TEXT,
        "colleges_level" TEXT, "county_id" TEXT, "county_name" TEXT, "department" TEXT, "doublehigh" TEXT, "dual_class" TEXT, "dual_class_name" TEXT, "f211" INTEGER,
        "f985" INTEGER, "hightitle" TEXT, "inner_rate" TEXT, "is_recruitment" TEXT, "level" TEXT, "level_name" TEXT, "name" TEXT, "nature" TEXT, "nature_name" TEXT,
        "outer_rate" TEXT, "province_id" TEXT, "province_name" TEXT, "rank" TEXT, "rank_type" TEXT, "rate" TEXT, "school_id" INTEGER, "school_type" TEXT, "tag_name" TEXT,
        "type" TEXT, "type_name" TEXT, "view_month" TEXT, "view_total" TEXT, "view_total_number" TEXT, "view_week" TEXT, "short" TEXT, "old_name" TEXT, "proid" TEXT);
        /*The table school_detail description is: '学校详情'.
    """

    # Convert to training data
    infer_data = process_infer_data(infer_origin_data, instruction)

    # Write the training data to a new JSON file
    with open("infer_data_for_Qwen.json", "w", encoding="utf-8") as f:
        json.dump(infer_data, f, ensure_ascii=False, indent=2)

    print("Done!")