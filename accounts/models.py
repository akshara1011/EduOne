"""
Custom Student User Model for ErVeda Platform.

We define a fully custom AbstractUser so we can add academic fields
(university, branch, semester, etc.) to the auth user from day one.
Django strongly recommends doing this before first migration.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class Student(AbstractUser):
    """
    Extended User model for B.Tech students.
    Inherits: username, email, password, first_name, last_name, is_active, is_staff
    """

    # --- Personal Info ---
    GENDER_CHOICES = [
        ('female', 'Female'),
        ('male', 'Male'),
        ('other', 'Other'),
    ]
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, blank=True, null=True
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_photo = models.ImageField(
        upload_to='profiles/', blank=True, null=True
    )
    college_name = models.CharField(max_length=200, blank=True, null=True)

    # --- Academic Info (FK populated after registration) ---
    university = models.ForeignKey(
        'academics.University',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='students'
    )
    regulation = models.ForeignKey(
        'academics.Regulation',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='students'
    )
    branch = models.ForeignKey(
        'academics.Branch',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='students'
    )
    current_year = models.PositiveSmallIntegerField(
        choices=[(1, '1st Year'), (2, '2nd Year'), (3, '3rd Year'), (4, '4th Year')],
        null=True, blank=True
    )
    current_semester = models.PositiveSmallIntegerField(
        choices=[(i, f'Semester {i}') for i in range(1, 9)],
        null=True, blank=True
    )

    # --- Platform Data ---
    study_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    total_questions_asked = models.PositiveIntegerField(default=0)
    profile_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.email})"

    @property
    def display_name(self):
        return self.get_full_name() or self.username

    @property
    def academic_info_complete(self):
        """Check if student has filled in academic details."""
        return all([
            self.university,
            self.branch,
            self.current_year,
            self.current_semester
        ])
