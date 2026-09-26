"""
Academic hierarchy models for ErVeda.

This is the core of the platform:
University → Regulation → Branch → Semester → Subject → Unit → Topic

All resources (notes, videos, PYQs, quizzes) are linked to these models.
"""

from django.db import models


class University(models.Model):
    """Represents a university/institution."""
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=20)  # e.g., JNTUH, VTU
    state = models.CharField(max_length=100)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='university_logos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'University'
        verbose_name_plural = 'Universities'
        ordering = ['name']

    def __str__(self):
        return f"{self.short_name} — {self.name}"


class Regulation(models.Model):
    """
    Academic regulation/pattern for a university.
    e.g., JNTUH R22, JNTUH R20, VTU 2021 Scheme
    """
    university = models.ForeignKey(
        University, on_delete=models.CASCADE, related_name='regulations'
    )
    name = models.CharField(max_length=50)       # e.g., R22
    year = models.PositiveSmallIntegerField()     # 2022
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-year']
        unique_together = ['university', 'name']

    def __str__(self):
        return f"{self.university.short_name} {self.name}"


class Branch(models.Model):
    """Engineering branch / department."""
    name = models.CharField(max_length=100)        # Computer Science and Engineering
    short_name = models.CharField(max_length=20)   # CSE
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.short_name} — {self.name}"


class Semester(models.Model):
    """
    A semester within a regulation and branch.
    e.g., JNTUH R22 > CSE > Semester 5
    """
    regulation = models.ForeignKey(
        Regulation, on_delete=models.CASCADE, related_name='semesters'
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name='semesters'
    )
    semester_number = models.PositiveSmallIntegerField()  # 1-8
    year_of_study = models.PositiveSmallIntegerField()    # 1-4

    class Meta:
        ordering = ['semester_number']
        unique_together = ['regulation', 'branch', 'semester_number']

    def __str__(self):
        return f"{self.regulation} | {self.branch.short_name} | Sem {self.semester_number}"


class Subject(models.Model):
    """A subject taught in a semester."""
    SUBJECT_TYPES = [
        ('theory', 'Theory'),
        ('lab', 'Laboratory'),
        ('elective', 'Elective'),
        ('project', 'Project'),
    ]

    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, related_name='subjects'
    )
    name = models.CharField(max_length=200)
    subject_code = models.CharField(max_length=20)
    credits = models.PositiveSmallIntegerField(default=3)
    subject_type = models.CharField(max_length=20, choices=SUBJECT_TYPES, default='theory')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.subject_code} — {self.name}"

    @property
    def university(self):
        return self.semester.regulation.university

    @property
    def branch(self):
        return self.semester.branch


class Unit(models.Model):
    """A unit within a subject."""
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name='units'
    )
    unit_number = models.PositiveSmallIntegerField()   # 1-5
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['unit_number']
        unique_together = ['subject', 'unit_number']

    def __str__(self):
        return f"Unit {self.unit_number}: {self.name} ({self.subject.subject_code})"


class Topic(models.Model):
    """A specific topic within a unit."""
    unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, related_name='topics'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} ({self.unit})"

    @property
    def subject(self):
        return self.unit.subject
