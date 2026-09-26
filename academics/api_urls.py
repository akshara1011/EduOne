from django.urls import path
from . import api_views

app_name = 'academics-api'

urlpatterns = [
    path('universities/', api_views.UniversityListView.as_view(), name='universities'),
    path('regulations/', api_views.RegulationListView.as_view(), name='regulations'),
    path('branches/', api_views.BranchListView.as_view(), name='branches'),
    path('semesters/', api_views.SemesterListView.as_view(), name='semesters'),
    path('subjects/', api_views.SubjectListView.as_view(), name='subjects'),
    path('units/', api_views.UnitListView.as_view(), name='units'),
    path('topics/', api_views.TopicListView.as_view(), name='topics'),
]
