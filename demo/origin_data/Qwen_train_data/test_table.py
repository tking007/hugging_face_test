import json

with open("/home/susu/下载/c_question/prep_c_train_data/prep_c_train_data/data/tables.json", "r", encoding="utf-8") as f:
    tables_data = json.load(f)
    for item in tables_data:
        # if item.get("db_id") == "common_1":
        # if item.get("table_names") == "Table_f4824235453d11e9bd5ff40f24344a08":
        if "Table_f4824235453d11e9bd5ff40f24344a08" in item:
            print("***")
            print(item)
            break

with open("test.json", "w", encoding="utf-8") as f:
    json.dump(tables_data, f, indent=2, ensure_ascii=False)
    print("Done!")


 #"Table_f4824235453d11e9bd5ff40f24344a08":