"""
PYQ models — Previous Year Question Papers and individual questions.
"""
from django.db import models


class QuestionPaper(models.Model):
    """A complete question paper from a previous exam."""

    EXAM_TYPES = [
        ('mid1', 'Mid-Term 1'),
        ('mid2', 'Mid-Term 2'),
        ('endsem', 'End Semester'),
        ('supply', 'Supplementary'),
        ('model', 'Model Paper'),
    ]

    subject = models.ForeignKey(
        'academics.Subject', on_delete=models.CASCADE, related_name='question_papers'
    )
    year = models.PositiveSmallIntegerField()
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES, default='endsem')
    pdf_file = models.FileField(upload_to='pyqs/papers/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year']
        unique_together = ['subject', 'year', 'exam_type']

    def __str__(self):
        return f"{self.subject.subject_code} — {self.year} {self.get_exam_type_display()}"


class PYQQuestion(models.Model):
    """An individual question extracted from a question paper."""

    QUESTION_TYPES = [
        ('long', 'Long Answer (10 marks)'),
        ('short', 'Short Answer (5 marks)'),
        ('very_short', 'Very Short Answer (2 marks)'),
        ('numerical', 'Numerical Problem'),
        ('mcq', 'Multiple Choice'),
        ('fill', 'Fill in the Blank'),
    ]

    paper = models.ForeignKey(
        QuestionPaper, on_delete=models.CASCADE, related_name='questions'
    )
    unit = models.ForeignKey(
        'academics.Unit', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='pyq_questions'
    )
    topic = models.ForeignKey(
        'academics.Topic', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='pyq_questions'
    )

    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='long')
    marks = models.PositiveSmallIntegerField(default=10)

    solution_text = models.TextField(blank=True)

    # Analytics
    frequency_count = models.PositiveIntegerField(default=1)
    importance_score = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-importance_score']

    def __str__(self):
        return f"Q: {self.question_text[:80]}..."

    def calculate_importance(self):
        """
        Calculate importance score based on:
        - frequency (how many times this question appeared)
        - recency (recent papers weighted more)
        - marks (higher marks = higher weight)
        """
        current_year = 2025
        paper_year = self.paper.year
        recency_score = max(0, 10 - (current_year - paper_year))

        marks_weight = min(self.marks / 10.0, 1.0)
        frequency_weight = min(self.frequency_count / 5.0, 1.0)

        score = (
            frequency_weight * 40 +
            (recency_score / 10) * 20 +
            marks_weight * 20 +
            20  # base score
        )
        self.importance_score = round(score, 2)
        return self.importance_score

    @property
    def importance_label(self):
        if self.importance_score >= 90:
            return ('Very Important', 'danger')
        elif self.importance_score >= 70:
            return ('Important', 'warning')
        elif self.importance_score >= 50:
            return ('Moderate', 'info')
        else:
            return ('Low Priority', 'secondary')
