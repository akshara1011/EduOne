"""
ErVeda URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

# ---------------------------------------------------------------------------
# Admin site branding (only visible to logged-in staff)
# ---------------------------------------------------------------------------
admin.site.site_header = 'ErVeda Administration'
admin.site.site_title = 'ErVeda Admin'
admin.site.index_title = 'Content Management'

urlpatterns = [
    # Admin — security handled by AdminRedirectMiddleware in settings.py
    path('admin/', admin.site.urls),

    # Landing page
    path('', TemplateView.as_view(template_name='landing.html'), name='home'),

    # Dedicated Web Admin Portal
    path('admin-portal/', include('admin_portal.urls', namespace='admin_portal')),

    # Apps
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('academics/', include('academics.urls')),
    path('resources/', include('resources.urls')),
    path('pyqs/', include('pyqs.urls')),
    path('quizzes/', include('quizzes.urls')),
    path('chat/', include('chatbot.urls')),
    path('scan/', include('question_solver.urls')),

    # REST API
    path('api/auth/', include('accounts.api_urls')),
    path('api/', include('academics.api_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
