# import json
# import time
# from tecent_fanyi import fanyi as translate
#
# with open(r"../CSpider/train.json", "r", encoding="utf-8") as f:
#     cspider_data = json.load(f)
#
# with open("sql_create_context_v4.json", "r", encoding="utf-8") as f:
#     v4_data = json.load(f)
#
# # 遍历两个数据集
# for x in cspider_data:
#     question_cspider = x["question"]
#     query_cspider = x["query"]
#
#     for y in v4_data:
#         answer_v4 = y["answer"]
#
#         # 比较 cspider 的 query 和 v4 的 answer
#         if query_cspider == answer_v4:
#             # 将 v4 中的 question 换为 cspider 中的 question
#             y["question"] = question_cspider
#         else:
#             translated_question = translate(y["question"])
#             y["question"] = translated_question
#             time.sleep(3)
#
# # 将修改后的 v4_data 写回文件
# with open("sql_create_context_v4.json", "w", encoding="utf-8") as f:
#     json.dump(v4_data, f, ensure_ascii=False, indent=2)


import json
import time
from tecent_fanyi import fanyi

with open(r"../CSpider/train.json", "r", encoding="utf-8") as f:
    cspider_data = json.load(f)

with open("sql_create_context_v4.json", "r", encoding="utf-8") as f:
    v4_data = json.load(f)

# 提取 v4 数据集中所有的 questions
v4_questions = [entry["question"] for entry in v4_data]

# 分批进行翻译
batch_size = 5  # 根据 QPS 限制设置合适的批量大小
for i in range(0, len(v4_questions), batch_size):
    batch = v4_questions[i:i + batch_size]

    # 批量翻译
    translated_batch = fanyi(batch)

    # 将翻译结果写回 v4 数据集
    for j, entry in enumerate(v4_data[i:i + batch_size]):
        entry["question"] = translated_batch[j]

    # 控制 QPS，根据 QPS 限制设置合适的等待时间
    time.sleep(1)

# 将修改后的 v4_data 写回文件
with open("data_sql.json", "w", encoding="utf-8") as f:
    json.dump(v4_data, f, ensure_ascii=False, indent=2)


