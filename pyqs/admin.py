"""
Admin configuration for Previous Year Questions (PYQs).
Manages QuestionPaper and PYQQuestion models.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import QuestionPaper, PYQQuestion


# ---------------------------------------------------------------------------
# Inline: PYQQuestion inside a QuestionPaper
# ---------------------------------------------------------------------------
class PYQQuestionInline(admin.TabularInline):
    model = PYQQuestion
    extra = 1
    fields = ('question_text', 'question_type', 'marks', 'unit', 'topic',
              'importance_score', 'frequency_count')
    readonly_fields = ('importance_score',)
    show_change_link = True


# ---------------------------------------------------------------------------
# QuestionPaper
# ---------------------------------------------------------------------------
@admin.register(QuestionPaper)
class QuestionPaperAdmin(admin.ModelAdmin):
    list_display = (
        '__str__', 'subject', 'year', 'exam_type',
        'question_count', 'is_verified', 'created_at',
    )
    list_filter = ('exam_type', 'is_verified', 'subject__semester__branch',
                   'subject__semester__regulation__university')
    search_fields = ('subject__name', 'subject__subject_code')
    list_editable = ('is_verified',)
    ordering = ('-year', 'subject')
    inlines = [PYQQuestionInline]
    date_hierarchy = 'created_at'

    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Questions'


# ---------------------------------------------------------------------------
# PYQQuestion
# ---------------------------------------------------------------------------
@admin.action(description='Recalculate importance scores')
def recalculate_importance(modeladmin, request, queryset):
    for q in queryset:
        q.calculate_importance()
        q.save(update_fields=['importance_score'])


@admin.register(PYQQuestion)
class PYQQuestionAdmin(admin.ModelAdmin):
    list_display = (
        'short_question', 'paper', 'question_type', 'marks',
        'frequency_count', 'importance_badge', 'created_at',
    )
    list_filter = ('question_type', 'paper__exam_type',
                   'paper__subject__semester__branch',
                   'paper__subject__semester__regulation__university')
    search_fields = ('question_text', 'paper__subject__name',
                     'paper__subject__subject_code')
    readonly_fields = ('importance_score',)
    actions = [recalculate_importance]
    ordering = ('-importance_score',)

    def short_question(self, obj):
        return obj.question_text[:80] + ('…' if len(obj.question_text) > 80 else '')
    short_question.short_description = 'Question'

    def importance_badge(self, obj):
        label, color = obj.importance_label
        colors = {
            'danger': '#dc3545', 'warning': '#fd7e14',
            'info': '#0dcaf0', 'secondary': '#6c757d',
        }
        hex_color = colors.get(color, '#6c757d')
        return format_html(
            '<span style="color:{}; font-weight:600;">{}</span>',
            hex_color, label,
        )
    importance_badge.short_description = 'Importance'

