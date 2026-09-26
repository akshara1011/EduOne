"""
URL routes for the ErVeda Admin Portal.
"""
from django.urls import path
from . import views

app_name = 'admin_portal'

urlpatterns = [
    # Auth
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),

    # Centralized Dashboard
    path('', views.dashboard, name='dashboard'),

    # Students Management
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.student_create, name='student_create'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('students/<int:student_id>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:student_id>/delete/', views.student_delete, name='student_delete'),
    path('students/<int:student_id>/toggle-status/', views.student_toggle_status, name='student_toggle_status'),

    # Academics: Universities
    path('universities/', views.university_list, name='university_list'),
    path('universities/add/', views.university_create, name='university_create'),
    path('universities/<int:pk>/edit/', views.university_edit, name='university_edit'),
    path('universities/<int:pk>/delete/', views.university_delete, name='university_delete'),

    # Academics: Regulations
    path('regulations/', views.regulation_list, name='regulation_list'),
    path('regulations/add/', views.regulation_create, name='regulation_create'),
    path('regulations/<int:pk>/edit/', views.regulation_edit, name='regulation_edit'),
    path('regulations/<int:pk>/delete/', views.regulation_delete, name='regulation_delete'),

    # Academics: Branches
    path('branches/', views.branch_list, name='branch_list'),
    path('branches/add/', views.branch_create, name='branch_create'),
    path('branches/<int:pk>/edit/', views.branch_edit, name='branch_edit'),
    path('branches/<int:pk>/delete/', views.branch_delete, name='branch_delete'),

    # Academics: Semesters
    path('semesters/', views.semester_list, name='semester_list'),
    path('semesters/add/', views.semester_create, name='semester_create'),
    path('semesters/<int:pk>/edit/', views.semester_edit, name='semester_edit'),
    path('semesters/<int:pk>/delete/', views.semester_delete, name='semester_delete'),

    # Academics: Subjects
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/add/', views.subject_create, name='subject_create'),
    path('subjects/<int:pk>/edit/', views.subject_edit, name='subject_edit'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),

    # Academics: Units & Topics
    path('units/', views.unit_list, name='unit_list'),
    path('units/add/', views.unit_create, name='unit_create'),
    path('units/<int:pk>/edit/', views.unit_edit, name='unit_edit'),
    path('units/<int:pk>/delete/', views.unit_delete, name='unit_delete'),

    path('topics/', views.topic_list, name='topic_list'),
    path('topics/add/', views.topic_create, name='topic_create'),
    path('topics/<int:pk>/edit/', views.topic_edit, name='topic_edit'),
    path('topics/<int:pk>/delete/', views.topic_delete, name='topic_delete'),

    # Resources: Notes & Videos
    path('notes/', views.note_list, name='note_list'),
    path('notes/add/', views.note_create, name='note_create'),
    path('notes/<int:pk>/edit/', views.note_edit, name='note_edit'),
    path('notes/<int:pk>/delete/', views.note_delete, name='note_delete'),
    path('notes/<int:pk>/toggle-approve/', views.note_toggle_approve, name='note_toggle_approve'),

    path('videos/', views.video_list, name='video_list'),
    path('videos/add/', views.video_create, name='video_create'),
    path('videos/<int:pk>/edit/', views.video_edit, name='video_edit'),
    path('videos/<int:pk>/delete/', views.video_delete, name='video_delete'),

    # PYQs: Question Papers & Questions
    path('papers/', views.paper_list, name='paper_list'),
    path('papers/add/', views.paper_create, name='paper_create'),
    path('papers/<int:pk>/edit/', views.paper_edit, name='paper_edit'),
    path('papers/<int:pk>/delete/', views.paper_delete, name='paper_delete'),

    path('questions/', views.question_list, name='question_list'),
    path('questions/add/', views.question_create, name='question_create'),
    path('questions/<int:pk>/edit/', views.question_edit, name='question_edit'),
    path('questions/<int:pk>/delete/', views.question_delete, name='question_delete'),

    # Quizzes & Quiz Questions
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('quizzes/add/', views.quiz_create, name='quiz_create'),
    path('quizzes/<int:pk>/edit/', views.quiz_edit, name='quiz_edit'),
    path('quizzes/<int:pk>/delete/', views.quiz_delete, name='quiz_delete'),

    path('quizzes/<int:quiz_id>/questions/', views.quiz_question_list, name='quiz_question_list'),
    path('quizzes/<int:quiz_id>/questions/add/', views.quiz_question_create, name='quiz_question_create'),
    path('quiz-questions/<int:pk>/edit/', views.quiz_question_edit, name='quiz_question_edit'),
    path('quiz-questions/<int:pk>/delete/', views.quiz_question_delete, name='quiz_question_delete'),

    # Platform Analytics & Intelligence
    path('analytics/', views.analytics, name='analytics'),
]
