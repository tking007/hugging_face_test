import json

with open("/home/susu/CSpider/train.json", "r", encoding="utf-8") as f:
    cspider_data = json.load(f)

# 提取 question 和 query 字段
new_data = [{"question": entry["question"], "query": entry["query"]} for entry in cspider_data]

# 将提取的数据写入新的 JSON 文件
with open("test_CSpider.json", "w", encoding="utf-8") as f:
    json.dump(new_data, f, ensure_ascii=False, indent=2)
