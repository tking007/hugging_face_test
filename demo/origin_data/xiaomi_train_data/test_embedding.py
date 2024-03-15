
def test_01():
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


def test_02():
    import torch.nn.functional as F
    from torch import Tensor
    from transformers import AutoTokenizer, AutoModel

    input_texts = [
        "中国的首都是哪里",
        "你喜欢去哪里旅游",
        "北京",
        "今天中午吃什么",
        "天津"
    ]

    tokenizer = AutoTokenizer.from_pretrained("thenlper/gte-large-zh")
    model = AutoModel.from_pretrained("thenlper/gte-large-zh")

    # Tokenize the input texts
    batch_dict = tokenizer(input_texts, max_length=512, padding=True, truncation=True, return_tensors='pt')

    outputs = model(**batch_dict)
    embeddings = outputs.last_hidden_state[:, 0]

    # (Optionally) normalize embeddings
    embeddings = F.normalize(embeddings, p=2, dim=1)
    scores = (embeddings[:1] @ embeddings[1:].T) * 100
    print(scores.tolist())

    # Combine the input_texts and scores into a list of tuples
    text_score_pairs = list(zip(input_texts[1:], scores.tolist()[0]))
    print(text_score_pairs)

    # Sort the list of tuples by the score (the second element of each tuple)
    sorted_text_score_pairs = sorted(text_score_pairs, key=lambda x: x[1], reverse=True)
    print(sorted_text_score_pairs)

    # Get the texts of the top five pairs
    top_five_texts = [text for text, score in sorted_text_score_pairs[:5]]

    print(top_five_texts)


def test_03():
    from modelscope.models import Model
    from modelscope.pipelines import pipeline
    from modelscope.utils.constant import Tasks

    model_id = "damo/nlp_gte_sentence-embedding_chinese-large"
    pipeline_se = pipeline(Tasks.sentence_embedding,
                           model=model_id,
                           sequence_length=512
                           ) # sequence_length 代表最大文本长度，默认值为128
    # 当输入包含“soure_sentence”与“sentences_to_compare”时，会输出source_sentence中首个句子与sentences_to_compare中每个句子的向量表示，以及source_sentence中首个句子与sentences_to_compare中每个句子的相似度。
    inputs = {
            "source_sentence": ["吃完海鲜可以喝牛奶吗?"],
            "sentences_to_compare": [
                "不可以，早晨喝牛奶不科学",
                "吃了海鲜后是不能再喝牛奶的，因为牛奶中含得有维生素C，如果海鲜喝牛奶一起服用会对人体造成一定的伤害",
                "吃海鲜是不能同时喝牛奶吃水果，这个至少间隔6小时以上才可以。",
                "吃海鲜是不可以吃柠檬的因为其中的维生素C会和海鲜中的矿物质形成砷"
            ]
        }

    result = pipeline_se(input=inputs)
    print (result)

    # 当输入仅含有soure_sentence时，会输出source_sentence中每个句子的向量表示以及首个句子与其他句子的相似度。
    inputs2 = {
            "source_sentence": [
                "不可以，早晨喝牛奶不科学",
                "吃了海鲜后是不能再喝牛奶的，因为牛奶中含得有维生素C，如果海鲜喝牛奶一起服用会对人体造成一定的伤害",
                "吃海鲜是不能同时喝牛奶吃水果，这个至少间隔6小时以上才可以。",
                "吃海鲜是不可以吃柠檬的因为其中的维生素C会和海鲜中的矿物质形成砷"
            ]
    }
    result = pipeline_se(input=inputs2)
    print (result)


def test_04():
    from mixedbread_ai import MixedbreadAi
    from sklearn.metrics.pairwise import cosine_similarity
    import os

    os.environ["MIXEDBREAD_API_KEY"] = "{MIXEDBREAD_API_KEY}"
    mxbai = MixedbreadAi()

    english_sentences = [
        'What is the capital of Australia?',
        'Canberra is the capital of Australia.'
    ]

    res = mxbai.embeddings(
         input=english_sentences,
         model="gte-large-zh"
    )
    embeddings = [entry.embedding for entry in res.data]

    similarities = cosine_similarity([embeddings[0]], [embeddings[1]])
    print(similarities)

def test_05():
    from sentence_transformers import SentenceTransformer
    from sentence_transformers.util import cos_sim

    sentences = ['That is a happy person', 'That is a very happy person']

    model = SentenceTransformer('thenlper/gte-large-zh')
    embeddings = model.encode(sentences)
    print(cos_sim(embeddings[0], embeddings[1]))


if __name__ == "__main__":
    test_02()
