import json

# Open the file and read it as a string
with open('train_data_for_Qwen.json', 'r') as f:
    datas = json.load(f)

    # Continue with your data processing
    res = []
    for idx, data in enumerate(datas[:1]):
        instructions = data['instructions']
        output_format = data['output_format']
        context = data['context']
        # conversations = data['conversations']

        question = data['conversations'].split("\"Question\": ")[1].split("\n")[0]
        sql_query = data['conversations'].split("\"SQLQuery\": ")[1].split("\n")[0]