from modelscope import AutoTokenizer, AutoModelForCausalLM
import gradio as gr
from loguru import logger
import sqlite3
import torch
from get_prompt import process_prompt

device = "cuda" if torch.cuda.is_available() else "cpu"
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
        chatbot.append((input, "Processing..."))
        prompt = process_prompt(input)
        model_inputs = tokenizer([prompt], return_tensors="pt").to(device)
        generated_ids = model.generate(model_inputs.input_ids, max_new_tokens=512)
        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        sql_query = response
        result = execute_sql(sql_query)
        if not result or result == "[]":
            model_inputs = tokenizer([input], return_tensors="pt").to(device)
            generated_ids = model.generate(model_inputs.input_ids, max_new_tokens=512)
            response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        else:
            response = "你的提问方式似乎存在问题哦，请换种方式提问试试。"
        chatbot[-1] = (str(input), str(response))  # Ensure chatbot is a list of tuples of strings
    except Exception as e:
        logger.error(f"Error in generating response: {str(e)}")
        chatbot[-1] = (str(input), "An error occurred while processing your request.")
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
        <p align="center"><img src="https://i.postimg.cc/gJ1sP6nj/image.png" style="height: 120px"/><p>""")
        # gr.Markdown("""<center><font size=8>基于Text-to-SQL的高考志愿填报辅助系统</center>""")
        gr.Markdown("""<center><b><font size=6 face='Sans-serif'>🎓🎓基于Text-to-SQL的高考志愿填报辅助系统🎓🎓</font></b></center>""")
        gr.Markdown(
            """\
        <center><font size=3>(This WebUI is based on Qwen-Chat, developed by Alibaba Cloud. \
        (本WebUI基于Qwen-Chat打造，实现聊天机器人功能。)</center>""")
        gr.Markdown("""\
        <center><font size=4>💝💝💝  Github
        &nbsp<a href="https://github.com/tking007/hugging_face_test.git">Github</a></center>""")

        # chatbot = gr.Chatbot(label='💋💋💋', elem_classes="control-height")
        chatbot = gr.Chatbot(label='answer', height=300)
        query = gr.Textbox(lines=2, label='Input')
        task_history = gr.State([])

        with gr.Row():
            empty_btn = gr.Button("🧹 Clear History (清除历史)")
            submit_btn = gr.Button("🚀 Submit (发送)")
            regen_btn = gr.Button("🤔 Regenerate (重试)")

        submit_btn.click(predict, [query, chatbot, task_history], [chatbot], show_progress=True)
        submit_btn.click(reset_user_input, [], [query])
        empty_btn.click(reset_state, [chatbot, task_history], outputs=[chatbot], show_progress=True)
        regen_btn.click(regenerate, [chatbot, task_history], [chatbot], show_progress=True)

        gr.Markdown("""\
        <font size=2>
        (☝️☝️☝️注：本应用程序使用的大模型可能存在一些局限性，包括但不限于对某些问题的理解和回答可能不准确。我们建议用户在得到错误答案时，尝试以不同的方式提问，或者用更具体的方式描述问题，以帮助模型更好地理解和回答。同时，我们强烈建议，用户不应传播及不应允许他人传播以下内容，包括但不限于:🚫⛔仇恨言论、暴力、色情、欺诈相关的有害信息。)
        """)

    return demo


if __name__ == "__main__":
    demo = create_app_interface()
    demo.queue().launch(server_name="0.0.0.0", server_port=None, share=True, inbrowser=True, debug=True)
