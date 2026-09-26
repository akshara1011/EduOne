"""Admin for question_solver"""
from django.contrib import admin
from .models import ScannedQuestion


@admin.register(ScannedQuestion)
class ScannedQuestionAdmin(admin.ModelAdmin):
    list_display = ['student', 'created_at', 'error']
    list_filter = ['created_at']
