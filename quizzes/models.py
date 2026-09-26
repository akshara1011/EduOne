"""
Quiz engine models — Quizzes, Questions, Attempts, and Analysis.
"""
from django.db import models
from django.conf import settings
import json


class Quiz(models.Model):
    """A quiz or mock test."""

    QUIZ_TYPES = [
        ('topic', 'Topic Quiz'),
        ('unit', 'Unit Test'),
        ('subject', 'Subject Mock Test'),
        ('full', 'Full Semester Mock'),
    ]

    DIFFICULTY_LEVELS = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
        ('mixed', 'Mixed'),
    ]

    title = models.CharField(max_length=200)
    quiz_type = models.CharField(max_length=20, choices=QUIZ_TYPES, default='topic')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='medium')

    subject = models.ForeignKey(
        'academics.Subject', on_delete=models.CASCADE, related_name='quizzes'
    )
    unit = models.ForeignKey(
        'academics.Unit', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='quizzes'
    )
    topic = models.ForeignKey(
        'academics.Topic', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='quizzes'
    )

    time_limit_minutes = models.PositiveSmallIntegerField(default=30)
    total_marks = models.PositiveSmallIntegerField(default=20)
    pass_marks = models.PositiveSmallIntegerField(default=10)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Quizzes'

    def __str__(self):
        return self.title

    @property
    def question_count(self):
        return self.questions.count()


class QuizQuestion(models.Model):
    """A question within a quiz."""

    QUESTION_TYPES = [
        ('mcq', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('fill', 'Fill in the Blank'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='mcq')

    # Options stored as JSON: {"A": "...", "B": "...", "C": "...", "D": "..."}
    options = models.JSONField(default=dict)
    correct_answer = models.CharField(max_length=10)  # "A", "B", "True", "False"
    explanation = models.TextField(blank=True)

    marks = models.PositiveSmallIntegerField(default=1)
    topic = models.ForeignKey(
        'academics.Topic', on_delete=models.SET_NULL, null=True, blank=True
    )
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:80]}"


class QuizAttempt(models.Model):
    """Records a student's attempt at a quiz."""

    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('timed_out', 'Timed Out'),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts'
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    score = models.PositiveSmallIntegerField(default=0)
    total_questions = models.PositiveSmallIntegerField(default=0)
    correct_count = models.PositiveSmallIntegerField(default=0)
    wrong_count = models.PositiveSmallIntegerField(default=0)

    # Student's answers: {"question_id": "selected_answer", ...}
    answers = models.JSONField(default=dict)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_taken_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.student.username} — {self.quiz.title} ({self.score})"

    @property
    def percentage(self):
        if self.quiz.total_marks:
            return round((self.score / self.quiz.total_marks) * 100, 1)
        return 0

    @property
    def passed(self):
        return self.score >= self.quiz.pass_marks


class QuizAnalysis(models.Model):
    """
    AI-powered analysis of a quiz attempt.
    Stores weak topics and personalized recommendations.
    """
    attempt = models.OneToOneField(
        QuizAttempt, on_delete=models.CASCADE, related_name='analysis'
    )
    weak_topics = models.JSONField(default=list)       # list of topic names
    strong_topics = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)   # list of recommendation strings
    ai_feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
