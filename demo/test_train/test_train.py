#!/usr/bin/env python
# coding: utf-8

# In[5]:


import subprocess
import os

result = subprocess.run('bash -c "source /etc/network_turbo && env | grep proxy"', shell=True, capture_output=True, text=True)
output = result.stdout
for line in output.splitlines():
    if '=' in line:
        var, value = line.split('=', 1)
        os.environ[var] = value


# In[11]:


import os
os.environ['CURL_CA_BUNDLE'] = ''


# In[6]:


get_ipython().system('pip install transformers')
get_ipython().system('pip install datasets')
get_ipython().system('pip install accelerate -U')
get_ipython().system('pip install transformers[torch]')
get_ipython().system('pip install sentencepiece')


# In[7]:


import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, DataCollatorWithPadding
from transformers import Seq2SeqTrainingArguments, Seq2SeqTrainer
from datasets import load_dataset, Dataset
from transformers import DataCollatorForSeq2Seq
from transformers import T5Tokenizer
from torch.utils.data import TensorDataset


# In[8]:


# 查看GPU的信息
get_ipython().system('nvidia-smi')


# In[14]:


# 加载微调所需的模型和tokenizer
model_name = "tscholak/2jrayxos"  # 替换为你的预训练模型的名称
tokenizer_name = "tscholak/2jrayxos"  # 替换为你的预训练模型的tokenizer名称
tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
model_checkpoint = "tscholak/2jrayxos"
model = AutoModelForSeq2SeqLM.from_pretrained(model_checkpoint, force_download=True, resume_download=False)


# In[16]:


# 初始化 T5 tokenizer
tokenizer = T5Tokenizer.from_pretrained("tscholak/2jrayxos")
import json


# 指向数据集文件的路径
# dataset_path = "/content/drive/MyDrive/CSpider"

# 读取训练数据
with open("train.json", "r", encoding="utf-8") as train_file:
    train_data = json.load(train_file)

# 读取验证数据
with open("dev.json", "r", encoding="utf-8") as validation_file:
    validation_data = json.load(validation_file)

# 现在你可以使用 train_data 和 validation_data 进行进一步的处理，以适应你的项目需求。


# In[17]:


# 修改预处理逻辑以适应CSpider数据集
def preprocess_cspider_data(data, tokenizer, max_source_length=128, max_target_length=64):
    formatted_data = []

    for example in data:
        question = example["question"]
        query = example["query"]

        # 根据模型输入的格式构建输入字符串
        input_string = f"question: {question} </s> sql: {query} </s>"

        # 使用 tokenizer 编码输入字符串
        input_encodings = tokenizer(
            input_string,
            truncation=True,
            padding="max_length",
            max_length=max_source_length,
            return_tensors="pt"
        )

        # 创建字典，包含输入、注意力掩码和目标
        formatted_data.append({
            "input_ids": input_encodings.input_ids[0],
            "attention_mask": input_encodings.attention_mask[0],
            "labels": tokenizer(query, truncation=True, padding="max_length", max_length=max_target_length, return_tensors="pt").input_ids[0],
        })

    return formatted_data

# 预处理训练数据
formatted_train_data = preprocess_cspider_data(train_data, tokenizer)

# 预处理验证数据
formatted_validation_data = preprocess_cspider_data(validation_data, tokenizer)

# 创建 Hugging Face Dataset
train_dataset = Dataset.from_dict({
    "input_ids": [item["input_ids"] for item in formatted_train_data],
    "attention_mask": [item["attention_mask"] for item in formatted_train_data],
    "labels": [item["labels"] for item in formatted_train_data]
}, split="train")

validation_dataset = Dataset.from_dict({
    "input_ids": [item["input_ids"] for item in formatted_validation_data],
    "attention_mask": [item["attention_mask"] for item in formatted_validation_data],
    "labels": [item["labels"] for item in formatted_validation_data]
}, split="validation")

print(train_dataset[1])
print(validation_dataset[1])


# In[18]:


import datasets
import random
import pandas as pd
from IPython.display import display, HTML

def show_random_elements(dataset, num_examples=2):
    assert num_examples <= len(dataset), "Can't pick more elements than there are in the dataset."
    picks = []
    for _ in range(num_examples):
        pick = random.randint(0, len(dataset)-1)
        while pick in picks:
            pick = random.randint(0, len(dataset)-1)
        picks.append(pick)

    df = pd.DataFrame(dataset[picks])
    for column, typ in dataset.features.items():
        if isinstance(typ, datasets.ClassLabel):
            df[column] = df[column].transform(lambda i: typ.names[i])
    display(HTML(df.to_html()))

show_random_elements(train_dataset)


# In[19]:


batch_size = 3
args = Seq2SeqTrainingArguments(
    "test-summarization",
    evaluation_strategy = "epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=batch_size,
    per_device_eval_batch_size=batch_size,
    weight_decay=0.01,
    save_total_limit=3,
    num_train_epochs=1,
    predict_with_generate=True,
    # fp16=True,
)


# In[20]:


data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)


# In[21]:


import nltk
import numpy as np

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    decoded_preds = tokenizer.batch_decode(predictions, skip_special_tokens=True)
    # Replace -100 in the labels as we can't decode them.
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

    # Rouge expects a newline after each sentence
    decoded_preds = ["\n".join(nltk.sent_tokenize(pred.strip())) for pred in decoded_preds]
    decoded_labels = ["\n".join(nltk.sent_tokenize(label.strip())) for label in decoded_labels]

    result = metric.compute(predictions=decoded_preds, references=decoded_labels, use_stemmer=True)
    # Extract a few results
    result = {key: value.mid.fmeasure * 100 for key, value in result.items()}

    # Add mean generated length
    prediction_lens = [np.count_nonzero(pred != tokenizer.pad_token_id) for pred in predictions]
    result["gen_len"] = np.mean(prediction_lens)

    return {k: round(v, 4) for k, v in result.items()}


# In[22]:


trainer = Seq2SeqTrainer(
    model,
    args,
    train_dataset=train_dataset,
    eval_dataset=validation_dataset,
    data_collator=data_collator,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)


# In[23]:


trainer.train()


# In[ ]:


# # 保存微调后的模型和分词器
# model.save_pretrained("my_finetuned_model")
# tokenizer.save_pretrained("my_finetuned_model")


# In[ ]:


# # 从保存的文件中加载微调后的模型和分词器
# model = BertForSequenceClassification.from_pretrained("my_finetuned_model")
# tokenizer = BertTokenizer.from_pretrained("my_finetuned_model")


# In[ ]:


get_ipython().system('huggingface-cli login')


# In[ ]:


get_ipython().system('sudo apt-get install git-lfs')


# In[ ]:


get_ipython().system('git lfs install')


# In[ ]:


get_ipython().system('huggingface-cli repo create tscholak/2jrayxos-CSpider-mrking_v2')


# In[ ]:


model.save_pretrained('tscholak/2jrayxos-CSpider-mrking_v2',push_to_hub=True)
tokenizer.save_pretrained('tscholak/2jrayxos-CSpider-mrking_v2',push_to_hub=True)

