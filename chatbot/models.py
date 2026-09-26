"""
Chatbot models — AI chat sessions grounded in student's syllabus.
"""
from django.db import models
from django.conf import settings


class ChatSession(models.Model):
    """
    A conversation session between a student and the AI chatbot.
    Tied to a subject/topic for syllabus-aware context.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions'
    )
    subject = models.ForeignKey(
        'academics.Subject', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='chat_sessions'
    )
    topic = models.ForeignKey(
        'academics.Topic', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='chat_sessions'
    )
    title = models.CharField(max_length=200, blank=True)  # auto-generated from first message
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_activity']

    def __str__(self):
        return f"Chat: {self.student.username} — {self.title or 'Untitled'}"

    @property
    def message_count(self):
        return self.messages.count()


class ChatMessage(models.Model):
    """A single message in a chat session."""

    ROLES = [
        ('user', 'User'),
        ('assistant', 'AI Assistant'),
    ]

    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name='messages'
    )
    role = models.CharField(max_length=20, choices=ROLES)
    content = models.TextField()

    # Sources used by AI to ground the answer (RAG citations)
    sources = models.JSONField(default=list)  # [{"type": "note", "id": 1, "title": "..."}]

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.role}] {self.content[:80]}"
