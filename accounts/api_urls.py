from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import api_views

urlpatterns = [
    path('register/', api_views.RegisterAPIView.as_view(), name='api-register'),
    path('profile/', api_views.ProfileAPIView.as_view(), name='api-profile'),
]
