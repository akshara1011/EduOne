from django.urls import path
from . import views

app_name = 'question_solver'

urlpatterns = [
    path('', views.scanner_home, name='home'),
    path('upload/', views.upload_question, name='upload'),
    path('result/<int:scan_id>/', views.scan_result, name='result'),
]
