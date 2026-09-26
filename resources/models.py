"""
Resources models: Notes, Videos, StudyMaterials.
All linked to Subject/Unit/Topic for precise filtering.
"""
from django.db import models
from django.conf import settings


class Note(models.Model):
    """Study notes — uploaded by admin/contributors."""

    NOTE_TYPES = [
        ('unit', 'Unit Notes'),
        ('topic', 'Topic Notes'),
        ('revision', 'Revision Notes'),
        ('short', 'Short Notes'),
        ('formula', 'Formula Sheet'),
        ('diagram', 'Diagrams'),
        ('cheatsheet', 'Cheat Sheet'),
        ('handwritten', 'Handwritten Notes'),
    ]

    title = models.CharField(max_length=300)
    note_type = models.CharField(max_length=20, choices=NOTE_TYPES, default='unit')
    description = models.TextField(blank=True)

    # Academic links
    subject = models.ForeignKey(
        'academics.Subject', on_delete=models.CASCADE, related_name='notes'
    )
    unit = models.ForeignKey(
        'academics.Unit', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='notes'
    )
    topic = models.ForeignKey(
        'academics.Topic', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='notes'
    )

    # Files
    pdf_file = models.FileField(upload_to='notes/pdfs/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='notes/thumbnails/', blank=True, null=True)

    # Metadata
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='uploaded_notes'
    )
    is_approved = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} [{self.note_type}]"

    @property
    def university(self):
        return self.subject.university


class Video(models.Model):
    """Curated YouTube videos linked to topics."""

    DIFFICULTY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    VIDEO_TYPES = [
        ('lecture', 'Lecture'),
        ('concept', 'Concept Explanation'),
        ('revision', 'Revision'),
        ('problem', 'Problem Solving'),
        ('animation', 'Animation'),
    ]

    title = models.CharField(max_length=300)
    youtube_url = models.URLField()
    youtube_id = models.CharField(max_length=20, blank=True)  # auto-extracted

    # Academic links
    subject = models.ForeignKey(
        'academics.Subject', on_delete=models.CASCADE, related_name='videos'
    )
    unit = models.ForeignKey(
        'academics.Unit', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='videos'
    )
    topic = models.ForeignKey(
        'academics.Topic', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='videos'
    )

    # Video metadata
    channel_name = models.CharField(max_length=200, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    language = models.CharField(max_length=50, default='English')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='intermediate')
    video_type = models.CharField(max_length=20, choices=VIDEO_TYPES, default='lecture')

    is_verified = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.subject.subject_code})"

    def save(self, *args, **kwargs):
        """Auto-extract YouTube ID from URL."""
        if self.youtube_url and not self.youtube_id:
            import re
            patterns = [
                r'(?:v=|/v/|youtu\.be/|/embed/)([a-zA-Z0-9_-]{11})',
            ]
            for pattern in patterns:
                match = re.search(pattern, self.youtube_url)
                if match:
                    self.youtube_id = match.group(1)
                    break
        super().save(*args, **kwargs)

    @property
    def thumbnail_url(self):
        if self.youtube_id:
            return f"https://img.youtube.com/vi/{self.youtube_id}/mqdefault.jpg"
        return ''

    @property
    def embed_url(self):
        if self.youtube_id:
            return f"https://www.youtube.com/embed/{self.youtube_id}"
        return ''

    @property
    def duration_formatted(self):
        if self.duration_seconds:
            mins = self.duration_seconds // 60
            secs = self.duration_seconds % 60
            return f"{mins}:{secs:02d}"
        return ''


class Bookmark(models.Model):
    """Student bookmarks for resources."""
    RESOURCE_TYPES = [
        ('note', 'Note'),
        ('video', 'Video'),
        ('pyq', 'PYQ Question'),
        ('quiz', 'Quiz'),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks'
    )
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    resource_id = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'resource_type', 'resource_id']
        ordering = ['-created_at']
