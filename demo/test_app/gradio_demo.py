from modelscope import AutoTokenizer, AutoModelForCausalLM
import gradio as gr
from loguru import logger
import sqlite3
import torch
from get_prompt import process_prompt

device = "cuda"
tokenizer = AutoTokenizer.from_pretrained("j869903116/mrking_qwn1.5_7B_chat_text_to_sql", revision='master')
model = AutoModelForCausalLM.from_pretrained("j869903116/mrking_qwn1.5_7B_chat_text_to_sql", revision='master',
                                             device_map="auto", torch_dtype="auto").eval()


def execute_sql(sql_query):
    conn = sqlite3.connect('../../../test_gaokao_data/schools/school_detail.sqlite')
    cursor = conn.cursor()
    try:
        cursor.execute(sql_query)
        result = cursor.fetchall()
        return result
    except Exception as e:
        return str(e)


def predict(input, chatbot, history):
    try:
        chatbot.append((input, ""))
        prompt = process_prompt(input)
        model_inputs = tokenizer([prompt], return_tensors="pt").to(device)
        generated_ids = model.generate(model_inputs.input_ids, max_new_tokens=512)
        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        sql_query = response
        result = execute_sql(sql_query)
        if not result:
            response = model.chat(tokenizer, input, history)
        else:
            response = model.chat(tokenizer, str(result), history)
        chatbot[-1] = (input, response)
        return chatbot, history
    except Exception as e:
        logger.error(f"Error in generating response: {str(e)}")
        return chatbot, history


def reset_user_input():
    return gr.update(value="")


def reset_state(chatbot, task_history):
    chatbot.clear()
    task_history.clear()
    return chatbot


def regenerate(_chatbot, _task_history):
    if not _task_history:
        yield _chatbot
        return
    item = _task_history.pop(-1)
    _chatbot.pop(-1)
    yield from predict(item[0], _chatbot, _task_history)


def create_app_interface():
    # https: // qianwen - res.oss - cn - beijing.aliyuncs.com / logo_qwen.jpg
    with gr.Blocks() as demo:
        gr.Markdown("""\
        <p align="center"><img src="https://i.postimg.cc/7hVDxvDR/0.avif" style="height: 80px"/><p>""")
        gr.Markdown("""<center><font size=8>基于Text-to-SQL的高考志愿填报辅助系统</center>""")
        gr.Markdown(
            """\
        <center><font size=3>This WebUI is based on Qwen-Chat, developed by Alibaba Cloud. \
        (本WebUI基于Qwen-Chat打造，实现聊天机器人功能。)</center>""")
        gr.Markdown("""\
        <center><font size=4>
        Qwen-7B <a href="https://modelscope.cn/models/qwen/Qwen-7B/summary">🤖 </a> | 
        <a href="https://huggingface.co/Qwen/Qwen-7B">🤗</a>&nbsp ｜ 
        Qwen-7B-Chat <a href="https://modelscope.cn/models/qwen/Qwen-7B-Chat/summary">🤖 </a> | 
        <a href="https://huggingface.co/Qwen/Qwen-7B-Chat">🤗</a>&nbsp ｜ 
        Qwen-14B <a href="https://modelscope.cn/models/qwen/Qwen-14B/summary">🤖 </a> | 
        <a href="https://huggingface.co/Qwen/Qwen-14B">🤗</a>&nbsp ｜ 
        Qwen-14B-Chat <a href="https://modelscope.cn/models/qwen/Qwen-14B-Chat/summary">🤖 </a> | 
        <a href="https://huggingface.co/Qwen/Qwen-14B-Chat">🤗</a>&nbsp ｜ 
        &nbsp<a href="https://github.com/QwenLM/Qwen">Github</a></center>""")

        chatbot = gr.Chatbot(label='Qwen-Chat', elem_classes="control-height")
        query = gr.Textbox(lines=2, label='Input')
        task_history = gr.State([])

        with gr.Row():
            empty_btn = gr.Button("🧹 Clear History (清除历史)")
            submit_btn = gr.Button("🚀 Submit (发送)")
            regen_btn = gr.Button("🤔️ Regenerate (重试)")

        submit_btn.click(predict, [query, chatbot, task_history], [chatbot], show_progress=True)
        submit_btn.click(reset_user_input, [], [query])
        empty_btn.click(reset_state, [chatbot, task_history], outputs=[chatbot], show_progress=True)
        regen_btn.click(regenerate, [chatbot, task_history], [chatbot], show_progress=True)

        gr.Markdown("""\
        <font size=2>Note: This demo is governed by the original license of Qwen. \
        We strongly advise users not to knowingly generate or allow others to knowingly generate harmful content, \
        including hate speech, violence, pornography, deception, etc. \
        (注：本演示受Qwen的许可协议限制。我们强烈建议，用户不应传播及不应允许他人传播以下内容，\
        包括但不限于仇恨言论、暴力、色情、欺诈相关的有害信息。)""")

    return demo


if __name__ == "__main__":
    demo = create_app_interface()
    demo.queue().launch(server_name="0.0.0.0", server_port=None, share=True, inbrowser=True)
