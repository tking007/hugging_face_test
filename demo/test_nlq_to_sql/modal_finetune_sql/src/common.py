# import io
# import sys
#
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')  # Windows系统默认的编码方式（GBK）无法正确编码某些Unicode字符

from modal import Image, Stub, NetworkFileSystem, Dict
import random
from typing import Optional
from pathlib import Path

VOL_MOUNT_PATH = Path("/vol")

WANDB_PROJECT = "test-finetune-modal"

MODEL_PATH = "/model"


def download_models():
    from transformers import LlamaForCausalLM, LlamaTokenizer
    #
    # # model_name = "openlm-research/open_llama_7b_v2"
    # from transformers import AutoModelForCausalLM, AutoTokenizer
    model_name = "FlagAlpha/Atom-7B"

    # model = LlamaForCausalLM.from_pretrained(model_name)
    model = LlamaForCausalLM.from_pretrained(model_name)
    model.save_pretrained(MODEL_PATH)

    # tokenizer = LlamaTokenizer.from_pretrained(model_name)
    tokenizer = LlamaTokenizer.from_pretrained(model_name)
    tokenizer.save_pretrained(MODEL_PATH)


openllama_image = (
    Image.micromamba()
    .micromamba_install(
        "cudatoolkit=11.7",
        "cudnn=8.1.0",
        "cuda-nvcc",
        channels=["conda-forge", "nvidia"],
    )
    .apt_install("git")
    .pip_install(
        "accelerate==0.18.0",
        "bitsandbytes==0.37.0",
        "bitsandbytes-cuda117==0.26.0.post2",
        "datasets==2.15.0",  # try to fix a bug in datasets
        "fire==0.5.0",
        "gradio==3.23.0",
        "peft @ git+https://github.com/huggingface/peft.git@e536616888d51b453ed354a6f1e243fecb02ea08",
        "transformers @ git+https://github.com/huggingface/transformers.git@a92e0ad2e20ef4ce28410b5e05c5d63a5a304e65",
        "torch==2.0.0",
        "torchvision==0.15.1",
        "sentencepiece==0.1.97",
        "llama-index",  # try to fix a bug in llama-index
        "sentence-transformers",
        "pydantic",  # replace x.y.z with the correct version
        "openai==0.28.0",  # add this to fix a bug in llama-index
        "langchain"  # add this to fix a bug in llama-index
    )
    .run_function(download_models)
    .pip_install("wandb==0.15.0")
)

stub = Stub(name="sql-finetune-bot", image=openllama_image)
stub.model_dict = Dict.new()
stub.data_dict = Dict.new()

output_vol = NetworkFileSystem.new(cloud="gcp").persisted("doppelbot-vol")


def generate_prompt_sql(input, context, output=""):
    return f"""You are a powerful text-to-SQL model. Your job is to answer questions about a database. You are given a question and context regarding one or more tables. 

You must output the SQL query that answers the question.

### Input:
{input}

### Context:
{context}

### Response:
{output}"""


def get_data_path(data_dir: str = "data_sql") -> Path:
    return VOL_MOUNT_PATH / data_dir / "data_sql.jsonl"


def get_model_path(data_dir: str = "data_sql", checkpoint: Optional[str] = None) -> Path:
    path = VOL_MOUNT_PATH / data_dir
    if checkpoint:
        path = path / checkpoint
    return path
