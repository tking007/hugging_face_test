import json
import sqlglot
import re
import sqlglot.errors


def replace_brackets_at_position(query):
    # Find all occurrences of '(亿)' in the query
    positions = [m.start() for m in re.finditer(r'\(亿\)', query)]
    for position in positions:
        # Replace each occurrence of '(亿)' with '（亿）'
        query = query[:position] + '（亿）' + query[position + 3:]
    return query


def preprocess_query(query, pattern):
    num_map = {'0': '零', '1': '一', '2': '二', '3': '三', '4': '四', '5': '五', '6': '六', '7': '七', '8': '八', '9': '九'}

    # 如果查询中包含 "40城"，则将其替换为 "四十城"
    query = query.replace('40城', '四十城')
    query = query.replace('(亿)', '（亿）')
    query = query.replace('一零零', '一百')
    query = query.replace('~', '-')
    query = query.replace('limit3', 'limit 3')
    query = query.replace('5A', '五A')

    # 使用正则表达式匹配select后面的三个连续的列名
    pattern_select = re.compile(r"(select\s+[\u4e00-\u9fa5]+\s+[\u4e00-\u9fa5]+\s+[\u4e00-\u9fa5]+)")
    # 使用正则表达式的sub方法替换匹配的字符串，将空格替换为逗号和空格
    query = pattern_select.sub(lambda m: m.group(1).replace(" ", ", "), query)
    processed_query = re.sub(pattern, lambda m: ''.join(num_map[i] for i in m.group(1)) + m.group(2), query)
    return processed_query


# Adjust the pattern to consider periods as valid following characters
pattern = re.compile(r'(?<=\w|\s|\.)(\d+)([\u4e00-\u9fa5]+)(?=\s|\.|$)')

# 打开并加载CSpider数据集
with open("../CSpider/train.json", "r", encoding="utf-8") as f:
    cspider_data = json.load(f)

# 打开并加载DUSQL数据集
with open("../DUSQL/train.json", "r", encoding="utf-8") as f:
    dusql_data = json.load(f)

    for entry in dusql_data:
        query = entry['query']
        # 使用正则表达式模式匹配query
        if pattern.search(query):
            # 使用中文字符和映射表替换匹配到的部分
            processed_query = preprocess_query(query, pattern)
            # print("####", query)
            try:
                # print("!!!!", query)
                # print("%%%%", processed_query)
                res = sqlglot.transpile(processed_query, identity=True)[0]
                entry["query"] = res
            except sqlglot.errors.ParseError as e:
                error_message = str(e)
                if "Invalid expression / Unexpected token" in error_message:
                    # 获取错误信息中的列号
                    col = int(re.search(r'Col: (\d+)', error_message).group(1))
                    # 检查列号对应的字符是否是括号
                    if query[col - 1] in '()':
                        # 将指定位置的英文括号替换为中文括号
                        origin_query = replace_brackets_at_position(query)
                        print("$$$", origin_query)
                        processed_query = preprocess_query(origin_query, pattern)
                        print("###", query)
                        res = sqlglot.transpile(processed_query, identity=True)[0]
                        print("@@@" , res)
        else:
            if ":" in query:
                res = sqlglot.transpile(processed_query, identity=True)[0]
                entry["query"] = res
            else:
                processed_query = preprocess_query(query, pattern)
                res = sqlglot.transpile(processed_query, identity=True)[0]
                entry["query"] = res


# 从CSpider数据集中提取question和query字段
new_cspider_data = [{"question": entry["question"], "answer": sqlglot.transpile(entry["query"])[0]} for entry in cspider_data]

# 从DUSQL数据集中提取question和query字段
new_dusql_data = [{"question": entry["question"], "answer": entry["query"]} for entry in dusql_data]

# 合并两个数据集
merged_data = new_cspider_data + new_dusql_data

# 将合并后的数据写入新的JSON文件
with open("merged_data.json", "w", encoding="utf-8") as f:
    json.dump(merged_data, f, ensure_ascii=False, indent=2)
