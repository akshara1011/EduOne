"""
Admin configuration for Progress app.
SubjectProgress is system-generated — shown read-only for monitoring.
"""

from django.contrib import admin
from .models import SubjectProgress


@admin.register(SubjectProgress)
class SubjectProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'overall_percentage', 'last_updated')
    list_filter = ('subject__semester__branch',
                   'subject__semester__regulation__university')
    search_fields = ('student__username', 'student__email', 'subject__name')
    readonly_fields = ('student', 'subject', 'overall_percentage', 'last_updated')
    ordering = ('-last_updated',)

    def has_add_permission(self, request):
        return False  # Progress is calculated automatically

    def has_change_permission(self, request, obj=None):
        return False  # Read-only monitoring

