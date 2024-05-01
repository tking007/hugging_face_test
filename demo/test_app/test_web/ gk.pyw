import os
import math
import time
from tkinter import font
import tkinter as tk
from tkinter.simpledialog import askstring
from tkinter import messagebox
from tkinter import StringVar

root = tk.Tk()

#主窗口初始化
root.overrideredirect(True)
width = 320
height = 120
scrw = root.winfo_screenwidth()
scrh = root.winfo_screenheight()
size_geo = '%dx%d+%d+%d' % (width, height, (scrw - width) / 2, (scrh - height) / 2)
root.geometry(size_geo)

#设置背景颜色和透明度
root.config(background="black")
root.attributes('-alpha', 0.7)


# 函数块

def on_double_click(event):  # 弹出输入提示窗口
    input_text = askstring("Input", "输入高考时间，例(2023-06-07):")  # 保存输入内容到文件
    try:
        time.strptime(strdate, "%Y-%m-%d")
        if input_text is not None:
            with open('gk.txt', 'w', encoding='utf-8') as f: f.write(input_text)
            f.close()
            global l
            l['text'] = js(input_text)
            return True
    except:
        messagebox.showerror('提示', '输入的数据类型有误')
        return False


def close_window(event): root.destroy()


def js(t):
    now = int(time.time())
    times = int(time.mktime(time.strptime(t, "%Y-%m-%d")))
    result = str(math.ceil((times - now) / 86400)) + "天"
    return result


root.bind('<ButtonRelease-1>', on_double_click)
root.bind('<Double-Button-3>', close_window)

#计算高考距离当前日期天数

# fo = open("gk.txt", "r+")
# gktime = fo.read()
gktime = '2024-06-07'
gktime = js(gktime)

label = tk.Label(root, text="高考倒计时", font=("汉仪正圆-45W", 30), fg="white", bg="black")
label.pack()

l = tk.Label(root, text=gktime, font=("汉仪正圆-45W", 30), fg="white", bg="black")
l.pack()

# 禁止alt+F4关闭窗口
root.protocol("WM_DELETE_WINDOW", lambda: None)

root.mainloop()
