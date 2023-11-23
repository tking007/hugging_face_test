import json
import sqlglot
import re


def preprocess_query(query):
    # 匹配数字和中文字符的混合部分
    pattern = re.compile(r'(?<=\s)(\d+)([\u4e00-\u9fa5]+)(?=\s|$)')
    # 使用中文字符替换匹配到的部分
    processed_query = re.sub(pattern, r'\2', query)
    return processed_query


# 打开并加载CSpider数据集
with open("../CSpider/train.json", "r", encoding="utf-8") as f:
    cspider_data = json.load(f)

# 打开并加载DUSQL数据集
with open("../DUSQL/train.json", "r", encoding="utf-8") as f:
    dusql_data = json.load(f)

# 从CSpider数据集中提取question和query字段
new_cspider_data = [{"question": entry["question"], "answer": sqlglot.transpile(entry["query"], identify=True)[0]} for entry in cspider_data]

# 从DUSQL数据集中提取question和query字段
new_dusql_data = [{"question": entry["question"], "answer": sqlglot.transpile(preprocess_query(entry["query"]), identify=True)[0]} for entry in dusql_data]

# 合并两个数据集
merged_data = new_cspider_data + new_dusql_data

# 将合并后的数据写入新的JSON文件
with open("merged_data.json", "w", encoding="utf-8") as f:
    json.dump(merged_data, f, ensure_ascii=False, indent=2)
