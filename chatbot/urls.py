from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chat_home, name='home'),
    path('new/', views.new_chat, name='new_chat'),
    path('<int:session_id>/', views.chat_session, name='session'),
    path('<int:session_id>/send/', views.send_message, name='send_message'),
]
