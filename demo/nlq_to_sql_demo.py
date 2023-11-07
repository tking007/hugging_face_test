# -*- coding: utf-8 -*-
"""NLQ_to_SQL_Demo.py

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OPYhIeMfVKotFOkf1ZlWwFMIEStGTn7v
"""

# Import Libraries*

import torch.nn.functional as F
import torch
from transformers import AutoTokenizer, AutoModel
import sqlite3
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sklearn.metrics.pairwise import cosine_similarity
import os

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

    endpoint = 'http://api.fanyi.baidu.com'
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


# Load Model

# Load model from HuggingFace Hub
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

# Load the model and tokenizer
tokenizer_decoder = AutoTokenizer.from_pretrained('tscholak/2jrayxos')
model_decoder = AutoModelForSeq2SeqLM.from_pretrained("tscholak/2jrayxos")

# tokenizer_decoder = AutoTokenizer.from_pretrained('tscholak/1zha5ono')
# model_decoder = AutoModelForSeq2SeqLM.from_pretrained("tscholak/1zha5ono")

'''
第一个模型：
这部分代码加载了名为 "sentence-transformers/all-MiniLM-L6-v2" 的预训练模型，该模型通常用于文本嵌入（text embedding）任务，例如文本相似度比较或信息检索。
这个模型由 Sentence Transformers 库提供，用于将文本转换为向量表示，以便进行各种自然语言处理任务。
第二个模型：
该模型是一个序列到序列（seq2seq）的语言模型，通常用于生成任务，例如问答、摘要生成、翻译等。它可以接受一个输入序列并生成一个相关的输出序列，因此适用于各种生成性任务。
原因是您可能需要同时处理文本嵌入和生成任务，所以需要加载两个不同的模型。这使您可以在同一应用程序中执行不同类型的自然语言处理任务。如果您只对其中一个任务感兴趣，可以只加载相关模型。
'''

# Function for Meanpooling


# Mean Pooling - Take attention mask into account for correct averaging

def mean_pooling(model_output, attention_mask):
    # First element of model_output contains all token embeddings
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(
        -1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


# Function to get Semantic Similarity


def encoder_decoder_1(query_sentence, table_names, tokenizer, model, cursor):
    # Tokenize query sentence, table names
    query_sentence_encoded = tokenizer(
        [query_sentence], padding=True, truncation=True, return_tensors='pt')
    table_names_encoded = tokenizer(
        table_names, padding=True, truncation=True, return_tensors='pt')

    # Compute token embeddings for query sentence, table names
    with torch.no_grad():
        query_sentence_output = model(**query_sentence_encoded)
        table_names_output = model(**table_names_encoded)

    # Perform pooling for query sentence, table names
    query_sentence_embedding = mean_pooling(
        query_sentence_output, query_sentence_encoded['attention_mask'])
    table_names_embeddings = mean_pooling(
        table_names_output, table_names_encoded['attention_mask'])

    # Normalize embeddings for query sentence, table names
    query_sentence_embedding = F.normalize(
        query_sentence_embedding, p=2, dim=1)
    table_names_embeddings = F.normalize(table_names_embeddings, p=2, dim=1)

    # Find the most similar table names by computing the cosine similarity between
    cosine_similarities_tables = torch.nn.functional.cosine_similarity(
        query_sentence_embedding, table_names_embeddings, dim=1)
    most_similar_table_names_indices = cosine_similarities_tables.argsort(
        descending=True)
    most_similar_table_names = [table_names[i]
                                for i in most_similar_table_names_indices]

    # Find the index of the highest matching table name by finding the maximum value
    max_similarity_table_index = cosine_similarities_tables.argmax()

    # Get the highest matching table name by using the index obtained above
    highest_matching_table_name = table_names[max_similarity_table_index]

    """
    cursor.execute(...): 这部分是使用SQLite数据库连接中的cursor对象执行SQL语句的一种方式。cursor对象用于执行SQL查询和操作数据库。
     PRAGMA: PRAGMA是SQLite数据库的一种特殊SQL语句，用于查询或设置数据库的各种参数和配置选项。 
    table_info: 这是一个PRAGMA命令，用于获取指定表的列信息，包括列名、数据类型等。
     "{highest_matching_table_name}": 这是一个Python字符串插值（f-string），用于将highest_matching_table_name的值嵌入到SQL
    查询中。highest_matching_table_name是一个代表数据库中某个表的名称的字符串。 
    所以，这行代码的目的是执行一个SQL查询，以获取表highest_matching_table_name的列信息，然后将结果存储在cursor
    对象中，以供后续处理和分析。这通常用于动态获取表的结构信息，以便在后续的数据库操作中使用。
    """

    # Find the column names of the highest matching table by querying the database
    # cursor.execute(f"PRAGMA table_info({highest_matching_table_name});")
    # 使用反引号 ` 或双引号 " 来引用表名和列名避免来与SQL关键字冲突
    cursor.execute(f"PRAGMA table_info(`{highest_matching_table_name}`);")
    highest_matching_table_column_names = [
        column_info[1] for column_info in cursor.fetchall()]

    highest_matching_table_column_names = ", ".join(
        highest_matching_table_column_names)

    highest_matching_table_column_names = list(
        highest_matching_table_column_names.split(", "))

    highest_matching_table_column_names = [column_name.replace(
        ' ', '_') for column_name in highest_matching_table_column_names]

    return highest_matching_table_name, highest_matching_table_column_names


# Function to Generate SQL Query


def encoder_decoder_2(query_sentence, database_name, highest_matching_table_name, highest_matching_table_column_names,
                      tokenizer_decoder, model_decoder):
    # Make input text in this format. input_text = "list name of film released in 2018 and rating more than 6? |
    # Movie: rating, year, title"
    input_text_1 = query_sentence + " | " + database_name + " | " + \
                   highest_matching_table_name + ": " + \
                   str(highest_matching_table_column_names)

    input_ids_1 = tokenizer_decoder.encode(input_text_1, return_tensors='pt')

    # Generate the output
    output_1 = model_decoder.generate(
        input_ids_1, max_length=128, num_beams=4, early_stopping=True)

    # Decode the output
    output_text_1 = tokenizer_decoder.decode(
        output_1[0], skip_special_tokens=True)

    print("嗯嗯", output_text_1)

    # Output: IMDB | select title from movie where rating > 6 and year =2018

    # split the output into two parts (sql and table name)
    output_text_1 = output_text_1.split("|")
    # sql_query = output_text_1[1].strip()
    if len(output_text_1) >= 2:
        sql_query = output_text_1[1].strip()
    else:
        sql_query = "No SQL query found"  # 或者您可以采取其他适当的措施

    # return the sql query
    return sql_query


# Funtion to Execute SQL Query


def sql_executor(sql_query, highest_matching_table_column_names, cursor):
    # convert list to lower case
    highest_matching_table_column_names = [
        x.lower() for x in highest_matching_table_column_names]

    # if s3 contains any of the words in lst1 then replace it with double quotes
    for i in highest_matching_table_column_names:
        if i in sql_query:
            sql_query = sql_query.replace(i, '"' + i + '"')

    # replace underscore with space
    sql_query = sql_query.replace("_", " ")
    # replace all single quotes with double quotes
    sql_query = sql_query.replace("'", '"')
    # Print the sql query
    print(sql_query)
    print("------")

    # Execute the sql
    try:
        cursor.execute(sql_query)
        result = cursor.fetchall()
        # Get column names using cursor.description
        column_names = [description[0] for description in cursor.description]
        print(column_names)  # Print column names
        print(result)  # Print the result

        # 创建一个Pandas DataFrame，将结果和列名组合起来
        # df = pd.DataFrame(result, columns=column_names)

        # res_1 = []
        # for i in result:
        #     for x in i:
        #         res_1.append(translate(str(x)))

        res_1 = []
        for j in column_names:
            res_1.append(translate(str(j)))

        # print(res_1)
        # print(res_2)

        res_2 = result + res_1

        df = pd.DataFrame(result, columns=res_2)
        # 打印DataFrame
        print("df:\n", df)

        # print the result
        print(res)
    except Exception as e:
        print("SQL query is not valid.")
        print(e)
        raise Exception


# Main Function


def main():
    while True:
        try:
            # Query sentence
            query = input("Enter question: ")

            query_sentence = translate(query)

            # Connect to database and fetch table names and column names
            conn = sqlite3.connect('actor_database.db')
            cursor = conn.cursor()

            # Get the filename that is connected above
            filename = conn.cursor().execute("PRAGMA database_list;").fetchall()[0][2]

            # Extract file name from file path
            database_name = os.path.basename(filename).split('.')[0]

            table_names = [table_info[0] for table_info in cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table';").fetchall()]

            column_names = []
            for table_name in table_names:
                cursor.execute(f"PRAGMA table_info(`{table_name}`);")
                column_names.extend([column_info[1]
                                     for column_info in cursor.fetchall()])

            highest_matching_table_name, highest_matching_table_column_names = encoder_decoder_1(
                query_sentence, table_names, tokenizer, model, cursor)

            sql_query = encoder_decoder_2(query_sentence, database_name, highest_matching_table_name,
                                          highest_matching_table_column_names, tokenizer_decoder, model_decoder)

            sql_executor(sql_query, highest_matching_table_column_names, cursor)

            # Close database connection
            conn.close()
        except Exception:
            print("Please try again!")


# Test with Natural Language Query

if __name__ == "__main__":
    main()