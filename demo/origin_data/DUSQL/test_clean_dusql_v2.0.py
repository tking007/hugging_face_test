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

    # num_map = {'0': '零', '1': '一', '2': '二', '3': '三', '4': '四', '5': '五', '6': '六', '7': '七', '8': '八', '9': '九'}
    # 如果查询中包含 "40城"，则将其替换为 "四十城"
    # query = query.replace('40城', '四十城')
    # query = query.replace('~', '-')
    # query = query.replace('5A', '五A')
    # query = query.replace('25-30岁会员数量', '\"25-30岁会员数量\"')
    # query = query.replace('31-35岁会员数量', '\"31-35岁会员数量\"')
    # query = query.replace('36-40岁会员数量', '\"36-40岁会员数量\"')
    # query = query.replace('41-45岁会员数量', '\"41-45岁会员数量\"')
    # query = query.replace('45~55岁会员数量', 'b.\"45~55岁会员数量\"')
    # query = query.replace('T1.25-30岁会员数量', 'T1.\"25-30岁会员数量\"')
    # query = query.replace('T1.31-35岁会员数量', 'T1.\"31-35岁会员数量\"')
    # query = query.replace('a.45-55岁会员数量', 'a.\"45-55岁会员数量\"')
    # query = query.replace('b.25-30岁会员数量', 'b.\"25-30岁会员数量\"')
    # query = query.replace('b.31-35岁会员数量', 'b.\"31-35岁会员数量\"')
    # query = query.replace('b.36-40岁会员数量', 'b.\"36-40岁会员数量\"')
    # query = query.replace('b.41-45岁会员数量', 'b.\"41-45岁会员数量\"')
    # query = query.replace('b.45~55岁会员数量', 'b.\"45~55岁会员数量\"')
    # query = query.replace('G2零峰会', 'b.\"G20峰会\"')
    # 使用正则表达式匹配select后面的三个连续的列名
    # 使用正则表达式的sub方法替换匹配的字符串，将空格替换为逗号和空格
    # if "岁" not in query:
    #     processed_query = re.sub(pattern, lambda m: ''.join(num_map[i] for i in m.group(1)) + m.group(2), query)
    #     processed_query = processed_query.replace('一零零', '一百')
    #     processed_query = processed_query.replace('五零零', '五百')
    #     processed_query = processed_query.replace('第二五届台湾金曲奖', '第二十五届台湾金曲奖"')
    #     return processed_query
    # else:
    #     return query
    return query


def quote_special_columns(query, pattern):
    # This function adds quotes around the matched text
    def quote_match(match):
        return f'\"{match.group(1)}\"'
    # Use the sub method to replace all matches in the query
    return pattern.sub(quote_match, query)


with open("train.json", "r", encoding="utf-8") as f:
    data = json.load(f)

    for entry in data:
        query = entry['query']

        # pattern = re.compile(r'(?<=\.|\s)(\d+[\u4e00-\u9fa5]+.*？)(?=\s|\.)')
        # first_cleaned_query = preprocess_query(query)
        # second_cleaned_query = quote_special_columns(first_cleaned_query, pattern)
        # s = sqlglot.transpile(second_cleaned_query, identify=True)[0]
        if "~" not in query and "T1" in query:
            if "强" in query:
                pattern = re.compile(r'(\b\d+[\u4e00-\u9fa5]+\d*[\u4e00-\u9fa5]*\b)')
                first_cleaned_query = preprocess_query(query)
                second_cleaned_query = quote_special_columns(first_cleaned_query, pattern)
                try:
                    s = sqlglot.transpile(second_cleaned_query)[0]
                except sqlglot.errors.ParseError as e:
                    print("111", second_cleaned_query)
                    print(e)
                    break
            else:
                pattern = re.compile(r'(\b\d+[\u4e00-\u9fa5]+(\d*[\u4e00-\u9fa5]*)*\b)')
                first_cleaned_query = preprocess_query(query)
                second_cleaned_query = quote_special_columns(first_cleaned_query, pattern)
                try:
                    s = sqlglot.transpile(second_cleaned_query)[0]
                except sqlglot.errors.ParseError as e:
                    print("222", second_cleaned_query)
                    print(e)
                    break
        else:
            if "~" in query:
                pattern = re.compile(r'(\b\d+~\d+\b|\b\d+~\d+[\u4e00-\u9fa5]+\b|\b\d{2}:\d{2}:\d{2}~\d{2}:\d{2}:\d{2}\b)')
                first_cleaned_query = preprocess_query(query)
                second_cleaned_query = quote_special_columns(first_cleaned_query, pattern)
                try:
                    s = sqlglot.transpile(second_cleaned_query)[0]
                except sqlglot.errors.ParseError as e:
                    print("333", second_cleaned_query)
                    print(e)
                    break
            else:
                pattern = re.compile(r'(\b\d+~\d+\b|\b\d+~\d+[\u4e00-\u9fa5]+\b|\b\d+[\u4e00-\u9fa5]+\d*[\u4e00-\u9fa5]*\b|\b\d{2}:\d{2}:\d{2}\b|\b\d+[a-zA-Z]+[\u4e00-\u9fa5]*)')
                first_cleaned_query = preprocess_query(query)
                second_cleaned_query = quote_special_columns(first_cleaned_query, pattern)
                try:
                    s = sqlglot.transpile(second_cleaned_query)[0]
                except sqlglot.errors.ParseError as e:
                    print("444", second_cleaned_query)
                    print(e)
                    break

