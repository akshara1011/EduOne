"""
Admin configuration for Resources app.
Manages Note, Video, and Bookmark models.
"""

from django.contrib import admin
from .models import Note, Video, Bookmark


# ---------------------------------------------------------------------------
# Custom admin actions
# ---------------------------------------------------------------------------
@admin.action(description='Approve selected notes (make visible to students)')
def approve_notes(modeladmin, request, queryset):
    queryset.update(is_approved=True)


@admin.action(description='Unapprove selected notes (hide from students)')
def unapprove_notes(modeladmin, request, queryset):
    queryset.update(is_approved=False)


@admin.action(description='Verify selected videos (make visible to students)')
def verify_videos(modeladmin, request, queryset):
    queryset.update(is_verified=True)


@admin.action(description='Unverify selected videos (hide from students)')
def unverify_videos(modeladmin, request, queryset):
    queryset.update(is_verified=False)


# ---------------------------------------------------------------------------
# Note
# ---------------------------------------------------------------------------
@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'note_type', 'subject', 'unit',
        'is_approved', 'view_count', 'download_count', 'created_at',
    )
    list_filter = ('note_type', 'is_approved',
                   'subject__semester__branch',
                   'subject__semester__regulation__university')
    search_fields = ('title', 'description', 'subject__name', 'subject__subject_code')
    list_editable = ('is_approved',)
    readonly_fields = ('view_count', 'download_count', 'created_at', 'updated_at')
    actions = [approve_notes, unapprove_notes]
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'note_type', 'description'),
        }),
        ('Academic Link', {
            'fields': ('subject', 'unit', 'topic'),
        }),
        ('Files', {
            'fields': ('pdf_file', 'thumbnail'),
        }),
        ('Publishing', {
            'fields': ('is_approved', 'uploaded_by'),
        }),
        ('Stats (read-only)', {
            'fields': ('view_count', 'download_count', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


# ---------------------------------------------------------------------------
# Video
# ---------------------------------------------------------------------------
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'subject', 'channel_name', 'difficulty',
        'video_type', 'is_verified', 'view_count', 'created_at',
    )
    list_filter = ('is_verified', 'difficulty', 'video_type', 'language',
                   'subject__semester__branch',
                   'subject__semester__regulation__university')
    search_fields = ('title', 'channel_name', 'subject__name', 'youtube_id')
    list_editable = ('is_verified',)
    readonly_fields = ('youtube_id', 'view_count', 'created_at')
    actions = [verify_videos, unverify_videos]
    ordering = ('-created_at',)

    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'youtube_url', 'youtube_id', 'channel_name'),
        }),
        ('Academic Link', {
            'fields': ('subject', 'unit', 'topic'),
        }),
        ('Metadata', {
            'fields': ('language', 'difficulty', 'video_type', 'duration_seconds'),
        }),
        ('Publishing', {
            'fields': ('is_verified',),
        }),
        ('Stats (read-only)', {
            'fields': ('view_count', 'created_at'),
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        """Auto-extract YouTube ID from URL on save."""
        import re
        if obj.youtube_url and not obj.youtube_id:
            match = re.search(
                r'(?:v=|/v/|youtu\.be/|/embed/)([a-zA-Z0-9_-]{11})',
                obj.youtube_url
            )
            if match:
                obj.youtube_id = match.group(1)
        super().save_model(request, obj, form, change)


# ---------------------------------------------------------------------------
# Bookmark (read-only reference — managed by the system)
# ---------------------------------------------------------------------------
@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('student', 'resource_type', 'resource_id', 'created_at')
    list_filter = ('resource_type',)
    search_fields = ('student__username', 'student__email')
    readonly_fields = ('student', 'resource_type', 'resource_id', 'created_at')
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False  # Bookmarks are created by students, not admin

