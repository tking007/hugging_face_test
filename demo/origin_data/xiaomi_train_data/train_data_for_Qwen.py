import json
import sqlite3
import os
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel


import requests
import random
import json
from hashlib import md5
import pandas as pd

pd.set_option('display.max_columns', 200)  # 设置显示列数
pd.set_option('display.max_rows', 100)  # 设置显示行数


# Generate salt and sign
def make_md5(s, encoding='utf-8'):
    return md5(s.encode(encoding)).hexdigest()


def translate(query):
    # Set your own appid/appkey.
    appid = '20231031001865589'
    appkey = 'HCaP53JoPIIw6urzCyAj'

    # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
    # from_lang = 'zh'
    # to_lang = 'en'
    from_lang = 'auto'
    to_lang = 'auto'

    endpoint = 'https://api.fanyi.baidu.com'
    path = '/api/trans/vip/translate'
    url = endpoint + path

    # query = '我们有多少演员'

    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)

    # Build request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

    # Send request
    r = requests.post(url, params=payload, headers=headers)
    result = r.json()

    # # Show response
    # print(json.dumps(result, indent=4, ensure_ascii=False))
    # print(result['trans_result'][0]['dst'])

    return result['trans_result'][0]['dst']


# Load model from HuggingFace Hub
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

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


# Mean Pooling - Take attention mask into account for correct averaging

def mean_pooling(model_output, attention_mask):
    # First element of model_output contains all token embeddings
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


def encoder_decoder_1(query_sentence, table_names_info, tokenizer, model, cursor):
    # Tokenize query sentence, table names
    query_sentence_encoded = tokenizer([query_sentence], padding=True, truncation=True, return_tensors='pt')
    table_names_encoded = tokenizer(table_names_info, padding=True, truncation=True, return_tensors='pt')

    # Compute token embeddings for query sentence, table names
    with torch.no_grad():
        query_sentence_output = model(**query_sentence_encoded)
        table_names_output = model(**table_names_encoded)

    # Perform pooling for query sentence, table names
    query_sentence_embedding = mean_pooling(query_sentence_output, query_sentence_encoded['attention_mask'])
    table_names_embeddings = mean_pooling(table_names_output, table_names_encoded['attention_mask'])

    # Normalize embeddings for query sentence, table names
    query_sentence_embedding = F.normalize(query_sentence_embedding, p=2, dim=1)
    table_names_embeddings = F.normalize(table_names_embeddings, p=2, dim=1)

    # Find the most similar table names by computing the cosine similarity between
    cosine_similarities_tables = torch.nn.functional.cosine_similarity(query_sentence_embedding, table_names_embeddings, dim=1)
    most_similar_table_names_indices = cosine_similarities_tables.argsort(descending=True)
    most_similar_table_names = [table_names[i] for i in most_similar_table_names_indices]

    # Find the index of the highest matching table name by finding the maximum value
    max_similarity_table_index = cosine_similarities_tables.argmax()

    # Get the highest matching table name by using the index obtained above
    highest_matching_table_name = table_names[max_similarity_table_index]

    # Find the column names of the highest matching table by querying the database
    # cursor.execute(f"PRAGMA table_info({highest_matching_table_name});")
    # 使用反引号 ` 或双引号 " 来引用表名和列名避免来与SQL关键字冲突
    cursor.execute(f"PRAGMA table_info(`{highest_matching_table_name}`);")
    highest_matching_table_column_names = [column_info[1] for column_info in cursor.fetchall()]

    highest_matching_table_column_names = ", ".join(highest_matching_table_column_names)

    highest_matching_table_column_names = list(highest_matching_table_column_names.split(", "))

    highest_matching_table_column_names = [column_name.replace(' ', '_') for column_name in highest_matching_table_column_names]

    return highest_matching_table_name, highest_matching_table_column_names


def convert_to_training_data(input_data, instruction, output_format):
    all_db_infos = json.load(open("tables.json", "r", encoding="utf-8"))

    training_data = []
    db_schemas = get_db_schemas(all_db_infos)

    for item in input_data[:2]:
        db_id = item['db_id']
        tables_name = item['tables_name']
        question = item['question']
        query = item['query']
        # query_sentence = translate(question)
        query_sentence = question
        # print(db_id, tables_name, question, query)

        # Check if the table information is already in memory
        if db_id not in db_schemas:
            continue

        # Connect to the database for each item
        # db_path = f"/home/susu/下载/c_question/prep_c_train_data/prep_c_train_data/data/database/{db_id}/{db_id}.sqlite"
        db_path = f"D:/c_question/prep_c_train_data/data/database/{db_id}/{db_id}.sqlite"
        # print(db_path)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get the filename that is connected above
        filename = conn.cursor().execute("PRAGMA database_list;").fetchall()[0][2]

        # Extract file name from file path
        database_name = os.path.basename(filename).split('.')[0]

        print("@@", tables_name)

        column_names = {}
        # for table_name in table_names:
        for table_name in tables_name:
            cursor.execute(f"PRAGMA table_info(`{table_name}`);")
            table_column_names = [columns[1] for columns in cursor.fetchall()]
            print("!!", table_column_infos)

            table_column_names = [column_info[1] for column_info in cursor.fetchall()]
            # 处理列名中的下划线，替换为空格
            table_column_names = [column_name.replace("_", " ") for column_name in table_column_names]
            column_names.extend(table_column_names)
            print("##", column_names)

        for table in db_schemas[db_id]["schema_items"]:
            if table["table_name"] not in tables_name:
                continue

            table_name_original = table["table_name_original"]
            table_name = table["table_name"]
            column_names = table["column_names"]
            column_names_original = table["column_names_original"]
            column_types = table["column_types"]
            print(table_name_original, table_name, db_id)

            schema_column = ""
            for column_name_original, column_name, column_type in zip(column_names_original, column_names, column_types):
                # print(column_name_original, table_name_original, column_type)
                cursor.execute(f"SELECT  DISTINCT `{column_name_original}` FROM `{table_name_original}`")
                # print(column_name_original, table_name_original, db_id)
                possible_values = [row[0] for row in cursor.fetchall()]

                print("sss", possible_values)
                highest_matching_table_column_info = encoder_decoder_1(query_sentence, possible_values, tokenizer, model, cursor)
                print("@@@", highest_matching_table_column_info)

                schema_column += f"The {column_name_original} field of {table_name} means {column_name} and has possible values as: {possible_values}.\n"

            schema_info = f"""
            CREATE TABLE {table_name_original} ({', '.join([f'{name} {column_type}' for name, column_type in zip(column_names_original, column_types)])});
            /*The table {table_name_original} description is: '{table_name}'.
            {schema_column}
            */
            """
            print(table_name_original, table_name, db_id)

            conversation = f"""
            "Question": {question}
            "SQLQuery": {query}
            """

            training_item = {
                "instructions": instruction,
                "output_format": output_format,
                "context": schema_info,
                "conversations": conversation
            }
            training_data.append(training_item)

        # Close the database connection after processing the data
        conn.close()

    return training_data


if __name__ == '__main__':
    origin_data = []
    with open("train.txt", "r", encoding="utf-8") as f:
        for line in f:
            origin_data.append(json.loads(line))

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
    with open("train_data_for_Qwen.json", "w", encoding="utf-8") as f:
        json.dump(training_data, f, ensure_ascii=False, indent=2)

    print("Done!")