import json
import csv

with open("llama_factory_train_data.json", "r", encoding="utf-8") as f:
    origin_data = json.load(f)

    with open("llama_factory_train_data.csv", "w", encoding="utf-8", newline='') as c_f:
        writer = csv.writer(c_f)
        writer.writerow(["question", "answer"])
        for item in origin_data:
            writer.writerow([item["conversations"][0]["value"], item["conversations"][1]["value"]])