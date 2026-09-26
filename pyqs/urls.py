from django.urls import path
from . import views
app_name = 'pyqs'
urlpatterns = [
    path('', views.paper_list, name='list'),
    path('important/', views.important_questions, name='important'),
    path('paper/<int:paper_id>/', views.paper_detail, name='paper_detail'),
    path('question/<int:question_id>/', views.question_detail, name='question_detail'),
]
