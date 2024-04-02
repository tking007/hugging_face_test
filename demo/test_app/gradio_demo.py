from modelscope import AutoTokenizer, AutoModelForCausalLM
import gradio as gr
from loguru import logger
import sqlite3
import demo.origin_data.xiaomi_train_data.process_infer_data.process_infer_data as pid


def load_model():
    device = "cuda"
    global tokenizer, model
    logger.info("Loading model...")
    tokenizer = AutoTokenizer.from_pretrained("j869903116/mrking_qwn1.5_7B_chat_text_to_sql", revision='master')
    model = AutoModelForCausalLM.from_pretrained("j869903116/mrking_qwn1.5_7B_chat_text_to_sql", revision='master',
                                                 device_map="auto", torch_dtype="auto").eval()
    logger.info("Model loaded successfully.")


def execute_sql(sql_query):
    # Connect to the database
    conn = sqlite3.connect('../test_gaokao_data/schools/school_detail.sqlite')
    cursor = conn.cursor()

    # Execute the SQL query and return the result
    try:
        cursor.execute(sql_query)
        result = cursor.fetchall()
        return result
    except Exception as e:
        return str(e)


def predict(input, chatbot, history):
    try:
        logger.info("Generating response...")
        chatbot.append((input, ""))
        prompt = pid(input)
        response, history = model.chat(tokenizer, prompt, history)
        sql_query = response
        result = execute_sql(sql_query)
        if not result:
            response, history = model.chat(tokenizer, input, history)
        else:
            response, history = model.chat(tokenizer, str(result), history)
        chatbot[-1] = (input, response)
        logger.info("Response generated successfully.")
        return chatbot, history
    except Exception as e:
        logger.error(f"Error in generating response: {str(e)}")
        return chatbot, history


def reset_user_input():
    return gr.update(value='')


if __name__ == "__main__":
    load_model()
    with gr.Blocks() as demo:
        gr.HTML("""<h1 align="center">基于Text-to-SQL的高考志愿辅助填报系统</h1>""")
        chatbot = gr.Chatbot()
        with gr.Row():
            with gr.Column(scale=4):
                with gr.Column(scale=12):
                    user_input = gr.Textbox(show_label=False, placeholder="Input...", lines=10)
                with gr.Column(min_width=32, scale=1):
                    submitBtn = gr.Button("Submit", variant="primary")

        history = gr.State([])
        past_key_values = gr.State(None)

        submitBtn.click(predict, [user_input, chatbot, history], [chatbot, history], show_progress=True)
        submitBtn.click(reset_user_input, [], [user_input])

    demo.queue().launch(share=True, inbrowser=True, debug=True, server_name='0.0.0.0')
