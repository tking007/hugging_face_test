import sqlglot
import re
import json
import sqlglot.errors


def preprocess_query(query):
    query = query.replace('(亿)', '（亿）')
    query = query.replace('limit3', 'limit 3')
    query = query.replace('desc 10', 'desc limit 10')
    pattern_select = re.compile(r"(select\s+[\u4e00-\u9fa5]+\s+[\u4e00-\u9fa5]+\s+[\u4e00-\u9fa5]+)")
    query = pattern_select.sub(lambda m: m.group(1).replace(" ", ", "), query)

    return query


def quote_special_columns(query, pattern):
    # This function adds quotes around the matched text
    def quote_match(match):
        return f'\"{match.group(1)}\"'

    # Use the sub method to replace all matches in the query
    return pattern.sub(quote_match, query)


# 打开并加载DUSQL数据集
with open("../DUSQL/train.json", "r", encoding="utf-8") as f:
    dusql_data = json.load(f)

    for entry in dusql_data:
        query = entry['query']

        if "~" not in query and "T1" in query:
            if "强" in query:
                # 匹配 2019年房地产企业500强
                pattern = re.compile(r'(\b\d+[\u4e00-\u9fa5]+\d*[\u4e00-\u9fa5]*\b)')
                first_cleaned_query = preprocess_query(query)
                second_cleaned_query = quote_special_columns(first_cleaned_query, pattern)
                try:
                    res = sqlglot.transpile(second_cleaned_query)[0]
                    entry["query"] = res
                except sqlglot.errors.ParseError as e:
                    print("111", second_cleaned_query)
                    print(e)
                    break
            else:
                pattern = re.compile(r'(\b\d+[\u4e00-\u9fa5]+(\d*[\u4e00-\u9fa5]*)*\b)')
                first_cleaned_query = preprocess_query(query)
                second_cleaned_query = quote_special_columns(first_cleaned_query, pattern)
                try:
                    res = sqlglot.transpile(second_cleaned_query)[0]
                    entry["query"] = res
                except sqlglot.errors.ParseError as e:
                    print("222", second_cleaned_query)
                    print(e)
                    break
        else:
            if "~" in query:
                pattern = re.compile(
                    r'(\b\d+~\d+\b|\b\d+~\d+[\u4e00-\u9fa5]+\b|\b\d{2}:\d{2}:\d{2}~\d{2}:\d{2}:\d{2}\b)')
                first_cleaned_query = preprocess_query(query)
                second_cleaned_query = quote_special_columns(first_cleaned_query, pattern)
                try:
                    res = sqlglot.transpile(second_cleaned_query)[0]
                    entry["query"] = res
                except sqlglot.errors.ParseError as e:
                    print("333", second_cleaned_query)
                    print(e)
                    break
            else:
                pattern = re.compile(
                    r'(\b\d+~\d+\b|\b\d+~\d+[\u4e00-\u9fa5]+\b|\b\d+[\u4e00-\u9fa5]+\d*[\u4e00-\u9fa5]*\b|\b\d{2}:\d{2}:\d{2}\b|\b\d+[a-zA-Z]+[\u4e00-\u9fa5]*)')
                first_cleaned_query = preprocess_query(query)
                second_cleaned_query = quote_special_columns(first_cleaned_query, pattern)
                try:
                    res = sqlglot.transpile(second_cleaned_query)[0]
                    entry["query"] = res
                except sqlglot.errors.ParseError as e:
                    print("444", second_cleaned_query)
                    print(e)
                    break

# 打开并加载CSpider数据集
with open("../CSpider/train.json", "r", encoding="utf-8") as f:
    cspider_data = json.load(f)

# 从CSpider数据集中提取question和query字段
new_cspider_data = [{"question": entry["question"], "answer": sqlglot.transpile(entry["query"])[0]} for entry in
                    cspider_data]

# 从DUSQL数据集中提取question和query字段
new_dusql_data = [{"question": entry["question"], "answer": entry["query"]} for entry in dusql_data]

# 合并两个数据集
merged_data = new_cspider_data + new_dusql_data

# 将合并后的数据写入新的JSON文件
with open("merged_data_v2.0.json", "w", encoding="utf-8") as f:
    json.dump(merged_data, f, ensure_ascii=False, indent=2)
