# views.py
import requests
from django.shortcuts import render

def index(request):
    response = requests.get('https://newsapi.org/v2/top-headlines?country=us&apiKey=your_api_key')
    news_list = response.json().get('articles', [])
    print(news_list)
    return render(request, 'index.html', {'news_list': news_list})