"""
Question solver models.
"""
from django.db import models
from django.conf import settings


class ScannedQuestion(models.Model):
    """A question uploaded by a student for AI solving."""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scanned_questions'
    )
    image = models.ImageField(upload_to='scans/', blank=True, null=True)
    ai_solution = models.TextField(blank=True)
    error = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Scan by {self.student.username} at {self.created_at}"
