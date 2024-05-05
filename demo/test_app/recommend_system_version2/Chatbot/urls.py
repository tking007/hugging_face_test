from django.urls import path
from . import views

urlpatterns = [
    # ... your other url patterns ...
    path('', views.qwen_chatbot, name='Qwen_Chatbot'),
]
