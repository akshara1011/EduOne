"""Stub models for progress app."""
from django.db import models
from django.conf import settings


class SubjectProgress(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subject_progress'
    )
    subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE)
    overall_percentage = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'subject']

    def __str__(self):
        return f"{self.student.username} - {self.subject.name}: {self.overall_percentage}%"


class LearningActivity(models.Model):
    """
    Tracks meaningful student learning actions for real calendar-day streak tracking.
    """
    ACTIVITY_TYPES = [
        ('quiz_submit', 'Quiz Completed'),
        ('ai_question', 'AI Question Asked'),
        ('scan_question', 'Question Scanned'),
        ('topic_study', 'Topic Studied'),
        ('note_view', 'Note Studied'),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='learning_activities'
    )
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Learning Activity'
        verbose_name_plural = 'Learning Activities'

    def __str__(self):
        return f"{self.student.username} - {self.get_activity_type_display()} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
