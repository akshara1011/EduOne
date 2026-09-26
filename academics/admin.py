"""
Admin for academic models — enhanced with search, filters, and import/export.
"""
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import University, Regulation, Branch, Semester, Subject, Unit, Topic


@admin.register(University)
class UniversityAdmin(ImportExportModelAdmin):
    list_display = ['short_name', 'name', 'state', 'is_active', 'created_at']
    list_filter = ['state', 'is_active']
    search_fields = ['name', 'short_name']


@admin.register(Regulation)
class RegulationAdmin(ImportExportModelAdmin):
    list_display = ['name', 'university', 'year', 'is_active']
    list_filter = ['university', 'is_active']
    search_fields = ['name']


@admin.register(Branch)
class BranchAdmin(ImportExportModelAdmin):
    list_display = ['short_name', 'name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'short_name']


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['regulation', 'branch', 'semester_number', 'year_of_study']
    list_filter = ['regulation__university', 'branch', 'semester_number']


@admin.register(Subject)
class SubjectAdmin(ImportExportModelAdmin):
    list_display = ['subject_code', 'name', 'semester', 'credits', 'subject_type', 'is_active']
    list_filter = [
        'semester__regulation__university',
        'semester__branch',
        'subject_type',
        'is_active'
    ]
    search_fields = ['name', 'subject_code']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'semester__regulation__university',
            'semester__branch'
        )


@admin.register(Unit)
class UnitAdmin(ImportExportModelAdmin):
    list_display = ['unit_number', 'name', 'subject']
    list_filter = ['subject__semester__regulation__university', 'subject__semester__branch']
    search_fields = ['name', 'subject__name']


@admin.register(Topic)
class TopicAdmin(ImportExportModelAdmin):
    list_display = ['name', 'unit', 'order']
    list_filter = ['unit__subject__semester__regulation__university']
    search_fields = ['name']
