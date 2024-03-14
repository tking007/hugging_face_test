import torch
from modelscope import snapshot_download, AutoModel, AutoTokenizer
from modelscope import GenerationConfig
model_dir = snapshot_download('j869903116/Qwen1.5_7B_text_to_sql_mrking', cache_dir='/home', revision='master')