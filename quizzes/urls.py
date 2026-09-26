from django.urls import path
from . import views
app_name = 'quizzes'
urlpatterns = [
    path('', views.quiz_list, name='list'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='detail'),
    path('quiz/<int:quiz_id>/start/', views.start_quiz, name='start_quiz'),
    path('attempt/<int:attempt_id>/', views.take_quiz, name='take_quiz'),
    path('attempt/<int:attempt_id>/save/', views.save_answer, name='save_answer'),
    path('attempt/<int:attempt_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('results/<int:attempt_id>/', views.quiz_results, name='results'),
    path('my-attempts/', views.my_attempts, name='my_attempts'),
]
