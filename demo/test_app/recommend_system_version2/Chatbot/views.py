from django.shortcuts import render

def qwen_chatbot(request):
    return render(request, 'Qwen_Chatbot.html')