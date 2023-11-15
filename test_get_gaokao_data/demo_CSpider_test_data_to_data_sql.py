import json
import time
import re
from demo.tencent_fanyi import fanyi

#  这是只需要CSpider数据集中两个字段的数据
# with open("/home/susu/CSpider/train.json", "r", encoding="utf-8") as f:
#     cspider_data = json.load(f)
#
# # 提取 question 和 query 字段
# new_data = [{"question": entry["question"], "query": entry["query"]} for entry in cspider_data]
#
# # 将提取的数据写入新的 JSON 文件
# with open("test_CSpider.json", "w", encoding="utf-8") as f:
#     json.dump(new_data, f, ensure_ascii=False, indent=2)


#  继续将answer字段中的英文\"issaquah\"翻译成中文
with open("../demo/data_sql.json", "r", encoding="utf-8") as f:
    datas = json.load(f)

for data in datas:
    sql_data = data["answer"]
    match = re.search(r'\"([a-zA-Z]{3,}\s*[a-zA-Z\s]*)\"', sql_data)
    if match:
        answer = match.group(1)
        if answer == "null":
            continue
        print(answer)
        data["answer"] = sql_data.replace(answer, fanyi([answer])[0])
        # data["answer"] = re.sub(re.escape(answer), fanyi([answer])[0], sql_data)
        print(data["answer"])
        time.sleep(1)

# # 将修改后的数据写回文件
with open("v1_data_sql.json", "w", encoding="utf-8") as f:
    json.dump(datas, f, ensure_ascii=False, indent=2)
