from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    path('syllabus/', views.syllabus_home, name='syllabus_home'),
    path('syllabus/<int:subject_id>/', views.subject_syllabus, name='subject_syllabus'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/<int:subject_id>/', views.subject_detail, name='subject_detail'),
    path('units/<int:unit_id>/', views.unit_detail, name='unit_detail'),
    path('topics/<int:topic_id>/', views.topic_detail, name='topic_detail'),

    # AJAX endpoints for cascading dropdowns
    path('ajax/regulations/', views.ajax_regulations, name='ajax_regulations'),
    path('ajax/branches/', views.ajax_branches, name='ajax_branches'),
    path('ajax/semesters/', views.ajax_semesters, name='ajax_semesters'),
    path('ajax/subjects/', views.ajax_subjects, name='ajax_subjects'),
]
