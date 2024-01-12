# from hanlp_restful import HanLPClient
from pyhanlp import *
import numpy as np
# from transformers import BertModel, BertTokenizer

# 初始化HanLP和BERT
# HanLP = HanLPClient('https://hanlp.hankcs.com/api', auth=None, language='zh')
# tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
# model = BertModel.from_pretrained('bert-base-chinese')


def extract_specific_relation(sentence):
    """ 使用HanLP抽取特定类型的依存关系 """
    doc = HanLP.parseDependency(sentence)
    specific_relations = []
    for word in doc.iterator():  # Traverse words in the sentence
        print(word.HEAD.LEMMA)
        if word.DEPREL == '定中关系':  # If the dependency relation is '定中关系'
            relation = [word.LEMMA, word.HEAD.LEMMA]
            if relation not in specific_relations:
                specific_relations.append(relation)

    print(specific_relations)

    # Join words in a meaningful way
    sentence = ''.join([f'{dependent}{head}' for dependent, head in specific_relations])
    return sentence


def calculate_match_score(question, table):
    """ 计算问题与表的匹配度 """
    column_names = table["column_names"]
    common_substrings = [word for word in extract_nouns(question) if word in column_names]
    common_substrings = [word for word in common_substrings if word not in ["这些", "什么", "有多少"]]
    match_score = np.mean([len(word) for word in common_substrings]) + max([len(word) for word in common_substrings]) + len(set("".join(common_substrings)))
    return match_score


def calculate_similarity(question, table):
    """ 使用BERT计算问题与表的相似度 """
    inputs = tokenizer(question, table["table_name"], return_tensors='pt')
    outputs = model(**inputs)
    similarity = np.dot(outputs[0][0][0].detach().numpy(), outputs[0][0][1].detach().numpy())
    return similarity


def find_best_match(question, tables):
    """ 找到与问题最匹配的表 """
    match_scores = [calculate_match_score(question, table) for table in tables]
    best_match_tables = [table for table, score in zip(tables, match_scores) if score == max(match_scores)]
    if len(best_match_tables) > 1:
        similarities = [calculate_similarity(question, table) for table in best_match_tables]
        best_match_table = best_match_tables[np.argmax(similarities)]
    else:
        best_match_table = best_match_tables[0]

    return best_match_table


if __name__ == "__main__":
    # find_best_match("小米有哪些产品", tables)
    # 使用这个函数抽取定中关系
    appos_relations = extract_specific_relation('你能不能告诉我在2018年7月9号买进或者散装的食品名称有几个啊。')
    print(appos_relations)