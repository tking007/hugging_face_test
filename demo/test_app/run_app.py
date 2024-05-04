# 启动Django服务的同时也启动Qwen_Chatbot服务
import subprocess
import os

# 启动Gradio应用
# os.chdir("../")  # 切换到Gradio应用的目录
gradio_process = subprocess.Popen("python Qwen_web_demo.py", shell=True)

# 启动Django应用
os.chdir("./recommend_system_version2")
django_process = subprocess.Popen("python manage.py runserver", shell=True)



# 等待两个应用都结束
django_process.wait()
gradio_process.wait()