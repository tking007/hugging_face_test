from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import GenerationConfig

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen-1_8B-Chat", trust_remote_code=True)

# Only Qwen-72B-Chat and Qwen-1_8B-Chat has system prompt enhancement now.
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen-1_8B-Chat", device_map="auto", trust_remote_code=True).eval()
# model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen-72B-Chat", device_map="auto", trust_remote_code=True).eval()

response, _ = model.chat(tokenizer, "部门中有多少人年龄大于56岁？", history=None, system="你是一名有着二十年工作经验的资深数据分析师身份擅长写SQL语句，请根据问题给出相应的SQL语句，需要保证SQL的正确性。")
print(response)

