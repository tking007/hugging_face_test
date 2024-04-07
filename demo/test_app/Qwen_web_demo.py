# Copyright (c) Alibaba Cloud.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

"""A simple web interactive chat demo based on gradio."""

from argparse import ArgumentParser
from threading import Thread

import gradio as gr
import torch
# from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from modelscope import AutoModelForCausalLM, AutoTokenizer
from transformers import TextIteratorStreamer
from get_prompt import process_prompt
import sqlite3

DEFAULT_CKPT_PATH = 'j869903116/mrking_qwn1.5_7B_chat_text_to_sql'  # modelscope库


# DEFAULT_CKPT_PATH = 'jtjt520j/mrking_Qwen1.5_7B_chat_text_to_sql'  # huggingface库


def execute_sql(sql_query):
    conn = sqlite3.connect('school_detail.sqlite')
    cursor = conn.cursor()
    try:
        cursor.execute(sql_query)
        result = cursor.fetchall()
        return result
    except Exception as e:
        return str(e)


def _get_args():
    parser = ArgumentParser()
    parser.add_argument("-c", "--checkpoint-path", type=str, default=DEFAULT_CKPT_PATH,
                        help="Checkpoint name or path, default to %(default)r")
    parser.add_argument("--cpu-only", action="store_true", help="Run demo with CPU only")

    parser.add_argument("--share", action="store_true", default=False,
                        help="Create a publicly shareable link for the interface.")
    parser.add_argument("--inbrowser", action="store_true", default=False,
                        help="Automatically launch the interface in a new tab on the default browser.")
    parser.add_argument("--server_port", type=int, default=8000,
                        help="Demo server port.")
    parser.add_argument("--server_name", type=str, default="127.0.0.1",
                        help="Demo server name.")

    args = parser.parse_args()
    return args


def _load_model_tokenizer(args):
    tokenizer = AutoTokenizer.from_pretrained(
        args.checkpoint_path, resume_download=True,
    )

    if args.cpu_only:
        device_map = "cpu"
        torch_dtype = "auto"
    else:
        device_map = "auto"
        torch_dtype = "auto"

    model = AutoModelForCausalLM.from_pretrained(
        args.checkpoint_path,
        device_map=device_map,
        torch_dtype=torch_dtype,
        resume_download=True,
    ).eval()
    model.generation_config.max_new_tokens = 2048  # For chat.

    return model, tokenizer


def _chat_stream(model, tokenizer, query, history):
    conversation = [
        {'role': 'system', 'content': 'You are a helpful assistant.'},
    ]
    for query_h, response_h in history:
        conversation.append({'role': 'user', 'content': query_h})
        conversation.append({'role': 'assistant', 'content': response_h})
    conversation.append({'role': 'user', 'content': query})
    inputs = tokenizer.apply_chat_template(
        conversation,
        add_generation_prompt=True,
        return_tensors='pt',
    )
    inputs = inputs.to(model.device)
    streamer = TextIteratorStreamer(tokenizer=tokenizer, skip_prompt=True, timeout=60.0, skip_special_tokens=True)
    generation_kwargs = dict(
        input_ids=inputs,
        streamer=streamer,
    )
    thread = Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()

    # for new_text in streamer:
    #     yield new_text

    full_response = ""
    for new_text in streamer:
        full_response += new_text
    return full_response


def new_result(result):
    new_result = f"  {result}  这是我的SQL查询结果。请帮我重新组织一下，以便我更好地理解。"
    return new_result


def _gc():
    import gc
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def _launch_demo(args, model, tokenizer):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def predict(_query, _chatbot, _task_history):
        print(f"User: {_query}")
        _chatbot.append((_query, ""))
        full_response = ""
        response = ""
        new_query = process_prompt(_query)
        full_response = _chat_stream(model, tokenizer, new_query, history=_task_history)
        result = execute_sql(full_response)
        print("result: ", result)
        print(f"full_response: {_chat_stream(model, tokenizer, new_query, history=_task_history)}")
        # if result:  # if the result is not empty
        #     new_res = new_result(result)
        #     model_inputs = tokenizer([new_res], return_tensors="pt").to(device)
        #     generated_ids = model.generate(model_inputs.input_ids, max_new_tokens=512)
        #     response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        # else:  # if the result is empty
        #     model_inputs = tokenizer([_query], return_tensors="pt").to(device)
        #     generated_ids = model.generate(model_inputs.input_ids, max_new_tokens=512)
        #     response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        # _chatbot[-1] = (_query, response)
        for new_text in _chat_stream(model, tokenizer, new_query, history=_task_history):
            response += new_text
        _chatbot[-1] = (_query, response)
        sql_query = response
        print("sql_query: ", sql_query)
        result = execute_sql(sql_query)  # execute_sql is your function to execute the SQL query
        print("result: ", result)
        if result:  # if the result is not empty
            new_res = _query + new_result(result)
            response = _chat_stream(model, tokenizer, new_res, history=_task_history)
            print("***", new_res)
            print("###", response)
            # model_inputs = tokenizer([new_res], return_tensors="pt").to(device)
            # generated_ids = model.generate(model_inputs.input_ids, max_new_tokens=512)
            # response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        else:  # if the result is empty
            response = _chat_stream(model, tokenizer, _query, history=_task_history)
            # model_inputs = tokenizer([_query], return_tensors="pt").to(device)
            # generated_ids = model.generate(model_inputs.input_ids, max_new_tokens=512)
            # response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            _chatbot[-1] = (_query, response)

        yield _chatbot
        full_response = response

        print(f"History: {_task_history}")
        _task_history.append((_query, full_response))
        print(f"Qwen1.5-Chat: {full_response}")

    def regenerate(_chatbot, _task_history):
        if not _task_history:
            yield _chatbot
            return
        item = _task_history.pop(-1)
        _chatbot.pop(-1)
        yield from predict(item[0], _chatbot, _task_history)

    def reset_user_input():
        return gr.update(value="")

    def reset_state(_chatbot, _task_history):
        _task_history.clear()
        _chatbot.clear()
        _gc()
        return _chatbot

    with gr.Blocks() as demo:
        gr.Markdown("""\
<p align="center"><img src="https://i.postimg.cc/gJ1sP6nj/image.png" style="height: 120px"/><p>""")
        gr.Markdown("""<center><b><font size=6 face='Sans-serif'>🎓🎓基于Text-to-SQL的高考志愿填报辅助系统🎓🎓</font></b></center>""")
        gr.Markdown(
            """\
<center><font size=3>This WebUI is based on Text-to-SQL, developed by Mrking. \
(本WebUI基于人工智能大模型打造，实现聊天机器人功能。)</center>""")
        gr.Markdown("""\
<center><font size=4>💝💝💝  Github
&nbsp<a href="https://github.com/tking007/hugging_face_test.git">Github</a></center>""")

        chatbot = gr.Chatbot(label='answer', elem_classes="control-height")
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
<font size=2>
(☝️☝️☝️注：本应用程序使用的大模型可能存在一些局限性，包括但不限于对某些问题的理解和回答可能不准确。\
我们建议用户在得到错误答案时，尝试以不同的方式提问，或者用更具体的方式描述问题，以帮助模型更好地理解和回答。\
同时，我们强烈建议，用户不应传播及不应允许他人传播以下内容，包括但不限于:🚫⛔仇恨言论、暴力、色情、欺诈相关的有害信息。)
""")

    demo.queue().launch(
        share=args.share,
        inbrowser=args.inbrowser,
        server_port=args.server_port,
        server_name=args.server_name,
    )


def main():
    args = _get_args()

    model, tokenizer = _load_model_tokenizer(args)

    _launch_demo(args, model, tokenizer)


if __name__ == '__main__':
    main()
