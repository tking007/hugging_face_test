import nltk
from nltk.tokenize import word_tokenize
import json

# 加载数据集
with open('train_data_for_Qwen.json', 'r') as f:
    data = json.load(f)

# 对每条数据进行tokenization
tokenized_data = [word_tokenize(str(item)) for item in data]

# 找出token数量最多的数据的token数量
max_token_count = max(len(item) for item in tokenized_data)

print(max_token_count)