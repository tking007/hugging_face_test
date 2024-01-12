import requests
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

Bearer = "E8C5CB3BC57F6AF43C8DB43B10F60448"

headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer E8C5CB3BC57F6AF43C8DB43B10F60448'}

def get_embeddings(texts, model):
    data = {'texts': texts, 'model': model}
    response = requests.post("https://api.embaas.io/v1/embeddings/", json=data, headers=headers)
    print(response.json())
    embeddings = [entry['embedding'] for entry in response.json()['data']]
    return np.array(embeddings)


query_text = "北京到上海三个小时"

corpus_texts = [
    "成都到天津五个小时",
    "花花真好看",
    "拉萨到大连十个小时",
]

model_name = "all-MiniLM-L6-v2"

query_embeddings = get_embeddings([query_text], model_name)
corpus_embeddings = get_embeddings(corpus_texts, model_name)

similarities = cosine_similarity(query_embeddings, corpus_embeddings)
print(similarities)
retrieved_doc_id = np.argmax(similarities)
print(corpus_texts[retrieved_doc_id])

# 获取相似度数组的索引
sorted_doc_ids = np.argsort(similarities[0])
print(sorted_doc_ids)

# 获取最相似的两个句子的索引
top_2_doc_ids = sorted_doc_ids[-2:]

# 获取最相似的三个句子的索引
top_3_doc_ids = sorted_doc_ids[-3:]

# 打印最相似的两个句子
print([corpus_texts[i] for i in top_2_doc_ids])

# 打印最相似的三个句子
print([corpus_texts[i] for i in top_3_doc_ids])