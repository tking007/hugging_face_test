import json

# 读取 JSON 数据
with open('school_detail.json', 'r', encoding='utf-8') as detail_file:
    data_detail = json.load(detail_file)

with open('school_name.json', 'r', encoding='utf-8') as name_file:
    data_name = json.load(name_file)

# 创建一个字典以便根据 school_id 查找 school_name 的数据
name_data_dict = {item['school_id']: item for item in data_name['data']}

# 更新 school_detail 数据
for detail_school in data_detail['data']:
    school_id = str(detail_school['school_id'])
    # print(school_id)
    name_data = name_data_dict.get(school_id)
    # print(name_data)
    if name_data:
        # 将 school_name 的数据合并到 school_detail
        # detail_school.update(name_data)
        detail_school['short'] = name_data.get('short', '')
        detail_school['old_name'] = name_data.get('old_name', '')
        detail_school['proid'] = name_data.get('proid', '')
        # print(name_data)
    # print(detail_school)


# 更新带有子目录路径的数据文件
with open('school_detail.json', 'w', encoding='utf-8') as detail_file:
    json.dump(data_detail, detail_file, ensure_ascii=False, indent=4)