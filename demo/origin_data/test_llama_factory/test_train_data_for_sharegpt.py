import json


def convert_to_training_data(input_data):
    training_data = []
    # for index, item in enumerate(input_data):
    for item in input_data:
        conversation = [
            {"from": "user", "value": item["question"]},
            {"from": "assistant", "value": item["answer"]}
        ]
        training_data.append({"conversations": conversation, "system": item["context"]})

    return training_data


if __name__ == '__main__':
    with open("../creat_table_test/cspider_sql_create_context.json", "r", encoding="utf-8") as f:
        origin_data = json.load(f)

    # 转换为训练数据
    training_data = convert_to_training_data(origin_data)

    # # 输出训练数据
    # print(json.dumps(training_data, ensure_ascii=False, indent=2))

    # 将提取的数据写入新的 JSON 文件
    with open("llama_factory_train_data.json", "w", encoding="utf-8") as f:
        json.dump(training_data, f, ensure_ascii=False, indent=2)
