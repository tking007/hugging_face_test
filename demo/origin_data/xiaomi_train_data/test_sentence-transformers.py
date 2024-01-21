# from transformers import AutoTokenizer, AutoModel
# import torch
#
#
# # Mean Pooling - Take attention mask into account for correct averaging
# def mean_pooling(model_output, attention_mask):
#     token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
#     input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
#     sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
#     sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
#     return sum_embeddings / sum_mask
#
#
# # Sentences we want sentence embeddings for
# sentences = [
#     "给我最高温度高于85的日期",
#     "max_temperature_f:[74, 78, 71, 75, 73, 72, 85, 88, 76].",
#     "date:['8/29/2013', '8/30/2013', '8/31/2013', '9/1/2013', '9/2/2013', '9/3/2013', '9/4/2013', '9/5/2013', '9/6/2013']",
# ]
#
# # Load AutoModel from huggingface model repository
# tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
# model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
#
# # Tokenize sentences
# encoded_input = tokenizer(
#     sentences, padding=True, truncation=True, max_length=128, return_tensors="pt"
# )
#
# # Compute token embeddings
# with torch.no_grad():
#     model_output = model(**encoded_input)
#
# # Perform pooling. In this case, mean pooling
# sentence_embeddings = mean_pooling(model_output, encoded_input["attention_mask"])
# print(sentence_embeddings)

# from sentence_transformers import SentenceTransformer
# import numpy as np
#
# # 加载预训练的句子嵌入模型
# model = SentenceTransformer('all-MiniLM-L6-v2')
#
# # 输入问题、字段值和枚举值
# question = "Give me a date with a maximum temperature above 85."
# field_values = ["max_temperature_f", "mean_wind_speed_mph", "min_temperature_f"]
# field_values = [i.replace('_', ' ') for i in field_values]
# print(field_values)
# enum_values = ["74, 78, 71", "68, 69, 64", "61, 60, 57", "85, 88, 76"]
#
# # 将问题、字段值和枚举值转换为嵌入向量
# question_embedding = model.encode([question])[0]
# field_embeddings = model.encode(field_values)
# enum_embeddings = model.encode(enum_values)
#
# # 计算问题嵌入向量与每个字段值和枚举值嵌入向量之间的余弦相似度
# field_similarities = [np.dot(question_embedding, field_embedding) / (np.linalg.norm(question_embedding) * np.linalg.norm(field_embedding)) for field_embedding in field_embeddings]
# enum_similarities = [np.dot(question_embedding, enum_embedding) / (np.linalg.norm(question_embedding) * np.linalg.norm(enum_embedding)) for enum_embedding in enum_embeddings]
#
# # 找到具有最高余弦相似度的字段值和枚举值
# most_similar_field_value = field_values[np.argmax(field_similarities)]
# most_similar_enum_value = enum_values[np.argmax(enum_similarities)]
#
# print("最相似的字段值：", most_similar_field_value)
# print("最相似的枚举值：", most_similar_enum_value)


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


def encoder_decoder_1(query_sentence, columns_info, tokenizer, model, cursor):
    # Tokenize query sentence, table names
    query_sentence_encoded = tokenizer([query_sentence], padding=True, truncation=True, return_tensors='pt')
    columns_info_encoded = tokenizer(columns_info, padding=True, truncation=True, return_tensors='pt')

    # Compute token embeddings for query sentence, table names
    with torch.no_grad():
        query_sentence_output = model(**query_sentence_encoded)
        columns_info_output = model(**columns_info_encoded)

    # Perform pooling for query sentence, table names
    query_sentence_embedding = mean_pooling(query_sentence_output, query_sentence_encoded['attention_mask'])
    columns_info_embeddings = mean_pooling(columns_info_output, columns_info_encoded['attention_mask'])

    # Normalize embeddings for query sentence, table names
    query_sentence_embedding = F.normalize(query_sentence_embedding, p=2, dim=1)
    columns_info_embeddings = F.normalize(columns_info_embeddings, p=2, dim=1)

    # Find the most similar table names by computing the cosine similarity between
    cosine_similarities_columns_info = torch.nn.functional.cosine_similarity(query_sentence_embedding, columns_info_embeddings, dim=1)
    most_similar_table_names_indices = cosine_similarities_columns_info.argsort(descending=True)
    most_similar_columns_info = [columns_info[i] for i in most_similar_table_names_indices]
    # print("query_sentence:", query_sentence)
    # print("most_similar_columns_info:", most_similar_columns_info)

    # Find the index of the highest matching table name by finding the maximum value
    max_similarity_columns_info_index = cosine_similarities_columns_info.argmax()

    # Get the highest matching table name by using the index obtained above
    highest_matching_table_name = columns_info[max_similarity_columns_info_index]

    # Find the column names of the highest matching table by querying the database
    # cursor.execute(f"PRAGMA table_info({highest_matching_table_name});")
    # 使用反引号 ` 或双引号 " 来引用表名和列名避免来与SQL关键字冲突
    cursor.execute(f"PRAGMA table_info(`{highest_matching_table_name}`);")
    highest_matching_table_column_names = [column_info[1] for column_info in cursor.fetchall()]

    highest_matching_table_column_names = ", ".join(highest_matching_table_column_names)

    highest_matching_table_column_names = list(highest_matching_table_column_names.split(", "))

    highest_matching_table_column_names = [column_name.replace(' ', '_') for column_name in highest_matching_table_column_names]

    # return highest_matching_table_name, highest_matching_table_column_names
    return most_similar_columns_info



def convert_to_training_data(input_data, instruction, output_format):
    all_db_infos = json.load(open("tables.json", "r", encoding="utf-8"))

    training_data = []
    db_schemas = get_db_schemas(all_db_infos)

    for item in input_data:
        db_id = item['db_id']
        tables_name = item['tables_name']
        question = item['question']
        query = item['query']
        query_sentence = question

        # Check if the table information is already in memory
        if db_id not in db_schemas:
            continue
        print(db_id, tables_name, question, query)

        db_path = f"D:/c_question/prep_c_train_data/data/database/{db_id}/{db_id}.sqlite"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # print("yyyyy", db_schemas[db_id]["schema_items"])
        # print("sss", tables_name)
        schema_info = ""
        for table in db_schemas[db_id]["schema_items"]:
            if table["table_name_original"] not in tables_name:
                continue

            table_name_original = table["table_name_original"]
            table_name = table["table_name"]
            column_names = table["column_names"]
            column_names_original = table["column_names_original"]
            column_types = table["column_types"]

            schema_column = ""
            for column_name_original, column_name, column_type in zip(column_names_original, column_names, column_types):
                cursor.execute(f"SELECT  DISTINCT `{column_name_original}` FROM `{table_name_original}`")
                possible_values = [str(row[0]) for row in cursor.fetchall()]

                if len(possible_values) == 0 or possible_values == ['']:
                    highest_matching_column_info = ''
                else:
                    highest_matching_column_info = encoder_decoder_1(query_sentence, possible_values, tokenizer, model, cursor)[:5]

                schema_column += f"The {column_name_original} field of {table_name} means {column_name} and has possible values as: {highest_matching_column_info}.\n"

            schema_info += f"""
            CREATE TABLE {table_name_original} ({', '.join([f'{name} {column_type}' for name, column_type in zip(column_names_original, column_types)])});
            /*The table {table_name_original} description is: '{table_name}'.
            {schema_column}
            */
            """

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