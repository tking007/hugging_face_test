# Finetuning LLaMa + Text-to-SQL 

This walkthrough shows you how to fine-tune LLaMa 2 7B on a Text-to-SQL dataset, and then use it for inference against
any database of structured data using LlamaIndex.

Check out our full blog here: https://medium.com/llamaindex-blog/easily-finetune-llama-2-for-your-text-to-sql-applications-ecd53640e10d

This code is taken and adapted from the Modal `doppel-bot` repo: https://github.com/modal-labs/doppel-bot.

### Stack

- LlamaIndex
- Modal
- Hugging Face datasets
- OpenLLaMa 
- Peft


### Setup

To get started, clone or fork this repo:

```bash
git clone https://github.com/run-llama/modal_finetune_sql.git
```

### Steps for Running

Please load the notebook `tutorial.ipynb` for full instructions.

```bash
cd modal_finetune_sql
jupyter notebook tutorial.ipynb
```

In the meantime you can run each step individually as below:

Loading data:
`modal run src.load_data_sql`

Finetuning:
`modal run --detach src.finetune_sql`

Inference:
`modal run src.inference_sql_llamaindex::main --query "Which city has the highest population?" --sqlite-file-path "nbs/cities.db"`

(Optional) Downloading model weights:
`modal run src.download_weights --output-dir out_model`
