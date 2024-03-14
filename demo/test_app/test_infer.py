from modelscope import AutoModelForCausalLM, AutoTokenizer
import torch
device = "cuda" # the device to load the model onto

model = AutoModelForCausalLM.from_pretrained(
    "j869903116/Qwen1.5_7B_text_to_sql_mrking",
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("j869903116/Qwen1.5_7B_text_to_sql_mrking")

for _ in range(100):

    prompt = str(input())
    messages = [
        {"role": "assistant", "content": "You are a MySQL expert.Output the final SQL query only."},
        {"role": "user", "content": prompt}
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(device)

    generated_ids = model.generate(
        model_inputs.input_ids,
        max_new_tokens=512
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    print(response)