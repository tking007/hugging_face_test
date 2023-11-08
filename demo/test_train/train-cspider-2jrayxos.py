#!/usr/bin/env python
# coding: utf-8

# <a href="https://colab.research.google.com/github/vanadnarayane26/Text_to_SQL_Spider-/blob/main/VVN_Text_to_sql.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# In[1]:


import subprocess
import os

result = subprocess.run('bash -c "source /etc/network_turbo && env | grep proxy"', shell=True, capture_output=True, text=True)
output = result.stdout
for line in output.splitlines():
    if '=' in line:
        var, value = line.split('=', 1)
        os.environ[var] = value


# In[2]:


#Installing libraries
get_ipython().system('pip install -q datasets')
get_ipython().system('pip install -q transformers')
get_ipython().system('pip install -q rouge_score')
get_ipython().system('pip install -q evaluate')
get_ipython().system('pip install transformers[torch]')
get_ipython().system('pip install seaborn')


# In[3]:


import os
os.environ['CURL_CA_BUNDLE'] = ''


# In[4]:


get_ipython().system('pip install scikit-learn')


# In[5]:


from transformers import Seq2SeqTrainingArguments, Seq2SeqTrainer
import pandas as pd
import nltk
import evaluate
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datasets import load_metric, Dataset
from nltk.tokenize import sent_tokenize
from sklearn.model_selection import train_test_split
# nltk.download('punkt')


# In[6]:


# import zipfile
# import shutil

# # 定义上传的ZIP文件名
# zip_file_name = "punkt.zip"

# # 解压ZIP文件
# with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
#     zip_ref.extractall("punkt_data")

# # 复制解压后的数据包到nltk_data目录
# shutil.copytree("punkt_data", "/path/to/nltk_data/tokenizers/punkt")


# In[7]:


# !pip install git+https://github.com/huggingface/datasets.git
get_ipython().system('pip install py-rouge')


# In[8]:


rouge_score = evaluate.load("rouge")


# In[9]:


df = pd.read_json('train.json')


# In[10]:


df.head()


# In[11]:


# Checking the sequence lengths for queries in dataset
l = []
for i in df['query']:
  l.append(len(i))

plt.figure(figsize = (10,6))
sns.distplot(l)
plt.show()


# In[12]:


# Checking the sequence length for questions in the dataset
l = []
for i in df['question']:
  l.append(len(i))

plt.figure(figsize = (10,6))
sns.distplot(l)
plt.show()


# In[13]:


df = df[['query','question']]


# In[14]:


# Splitting the dataset into training and validation set
train_df, val_df = train_test_split(df,test_size = 0.1, random_state = 21)
print(train_df.shape)
print(val_df.shape)


# In[15]:


# Converting the pandas dataframe to huggingface datasets and drooping the index columns generated
train_dataset = Dataset.from_pandas(train_df)
val_dataset = Dataset.from_pandas(val_df)
train_dataset = train_dataset.remove_columns(['__index_level_0__'])
val_dataset = val_dataset.remove_columns(['__index_level_0__'])
print(train_dataset)
print(val_dataset)


# In[16]:


train_dataset['query'][1]


# In[17]:


# downloading model from the checkpoint
from transformers import AutoTokenizer
model_checkpoint = "tscholak/2jrayxos"
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)


# In[18]:


# Preprocessing and defining the sequence length for training the models
max_input_length = 256
max_target_length = 256


def preprocess_function(examples):
    model_inputs = tokenizer(
        examples['question'],
        max_length=max_input_length,
        truncation=True, padding = 'max_length'
    )
    labels = tokenizer(text_target = examples['query'], max_length=max_target_length, truncation=True,padding = 'max_length')
    model_inputs["labels"] = labels["input_ids"]
    model_inputs["labels_mask"] = labels["attention_mask"]
    return model_inputs


# In[19]:


tokenized_train_datasets = train_dataset.map(preprocess_function, batched=True)


# In[20]:


tokenized_val_datasets = val_dataset.map(preprocess_function, batched=True)


# In[21]:


tokenized_train_datasets = tokenized_train_datasets.remove_columns(['query','question'])
tokenized_val_datasets = tokenized_val_datasets.remove_columns(['query','question'])


# In[22]:


from transformers import AutoModelForSeq2SeqLM, DataCollatorForSeq2Seq, Seq2SeqTrainer, Seq2SeqTrainingArguments

model = AutoModelForSeq2SeqLM.from_pretrained(model_checkpoint)


# In[23]:


data_collator = DataCollatorForSeq2Seq(model = model,tokenizer = tokenizer,label_pad_token_id=-100)


# In[24]:


import os
os.environ["CUDA_LAUNCH_BLOCKING"] = "1"


# In[25]:


batch_size = 3
learning_rate = 1e-5
args = Seq2SeqTrainingArguments(
    "test-summary",
    evaluation_strategy = "epoch",
    learning_rate=learning_rate,
    per_device_train_batch_size=batch_size,
    per_device_eval_batch_size=batch_size,
    weight_decay=0.01,
    save_total_limit=3,
    num_train_epochs=3,
    predict_with_generate=True,
    fp16=False,
    push_to_hub = False
)


# In[26]:


def postprocess_text(preds, labels):
    preds = [pred.strip() for pred in preds]
    labels = [[label.strip()] for label in labels]

    return preds, labels

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    decoded_preds = tokenizer.batch_decode(predictions, skip_special_tokens=True)
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
    decoded_preds = ["\n".join(sent_tokenize(pred.strip())) for pred in decoded_preds]
    decoded_labels = ["\n".join(sent_tokenize(label.strip())) for label in decoded_labels]
    result = rouge_score.compute(
        predictions=decoded_preds, references=decoded_labels, use_stemmer=True
    )
    result = {key: value * 100 for key, value in result.items()}
    return {k: round(v, 4) for k, v in result.items()}


# In[27]:


trainer = Seq2SeqTrainer(
    model,
    args,
    train_dataset=tokenized_train_datasets,
    eval_dataset=tokenized_val_datasets,
    data_collator=data_collator,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,

)


# In[ ]:


trainer.train()


# In[ ]:


get_ipython().system('huggingface-cli login')


# In[ ]:


get_ipython().system('sudo apt-get install git-lfs')


# In[ ]:


get_ipython().system('git lfs install')


# In[ ]:


get_ipython().system('huggingface-cli repo create tscholak/2jrayxos-CSpider-mrking_v1')


# In[ ]:


model.save_pretrained('tscholak/2jrayxos-CSpider-mrking_v1',push_to_hub=True)
tokenizer.save_pretrained('tscholak/2jrayxos-CSpider-mrking_v1',push_to_hub=True)

