"""
Admin registration for Student model.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Student


@admin.register(Student)
class StudentAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name',
                    'university', 'branch', 'current_semester', 'profile_completed', 'date_joined']
    list_filter = ['university', 'branch', 'current_year', 'current_semester', 'profile_completed']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']

    fieldsets = UserAdmin.fieldsets + (
        ('Academic Info', {
            'fields': ('university', 'regulation', 'branch', 'current_year',
                       'current_semester', 'college_name', 'phone_number')
        }),
        ('Platform Stats', {
            'fields': ('study_streak', 'total_questions_asked', 'profile_completed', 'profile_photo')
        }),
    )
