"""
Academic hierarchy models for ErVeda.

This is the core of the platform:
University → Regulation → Branch → Semester → Subject → Unit → Topic

All resources (notes, videos, PYQs, quizzes) are linked to these models.
"""

from django.db import models


class University(models.Model):
    """Represents a university or affiliated college/institution."""
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=20)  # e.g., JNTUH, OU, VTU
    parent_university = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='affiliated_colleges',
        help_text="Parent university if this is an affiliated college/institution (e.g. JNTUH)."
    )
    state = models.CharField(max_length=100)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='university_logos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'University / College'
        verbose_name_plural = 'Universities & Colleges'
        ordering = ['name']

    def __str__(self):
        if self.parent_university:
            return f"{self.short_name} — {self.name} (Affiliated to {self.parent_university.short_name})"
        return f"{self.short_name} — {self.name}"

    @property
    def is_affiliated_college(self):
        return self.parent_university is not None


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

    branches = models.ManyToManyField(
        'Branch', blank=True, related_name='regulations'
    )

    class Meta:
        ordering = ['-year']
        unique_together = ['university', 'name']

    def __str__(self):
        return f"{self.university.short_name} {self.name}"

    def get_branches(self):
        """Get all branches associated with this regulation (direct M2M or via semesters)."""
        return Branch.objects.filter(
            models.Q(id__in=self.branches.values_list('id', flat=True)) |
            models.Q(semesters__regulation=self)
        ).distinct()


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
    e.g., JNTUH R22 > CSE > Semester 5 (3-1)
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
        return f"{self.regulation} | {self.branch.short_name} | Sem {self.semester_number} ({self.code})"

    @property
    def name(self):
        return f"Semester {self.semester_number}"

    @property
    def code(self):
        """Standard B.Tech semester code like 1-1, 1-2, 2-1, 2-2, 3-1, 3-2, 4-1, 4-2."""
        year = (self.semester_number + 1) // 2
        sem = 2 if self.semester_number % 2 == 0 else 1
        return f"{year}-{sem}"

    @property
    def academic_year_title(self):
        """Human-readable academic year and semester title."""
        year = (self.semester_number + 1) // 2
        sem = 2 if self.semester_number % 2 == 0 else 1
        year_romans = {1: 'I', 2: 'II', 3: 'III', 4: 'IV'}
        sem_romans = {1: 'I', 2: 'II'}
        return f"{year_romans.get(year, str(year))} Year {sem_romans.get(sem, str(sem))} Semester"


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
    ltp = models.CharField(max_length=20, default='3-0-0', blank=True, help_text="L-T-P format (e.g. 3-0-0)")
    subject_type = models.CharField(max_length=20, choices=SUBJECT_TYPES, default='theory')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.subject_code} — {self.name}"

    @property
    def code(self):
        return self.subject_code

    @property
    def university(self):
        return self.semester.regulation.university

    @property
    def branch(self):
        return self.semester.branch

    def get_or_create_syllabus(self):
        syllabus, _ = Syllabus.objects.get_or_create(subject=self)
        return syllabus


class Syllabus(models.Model):
    """Complete syllabus structure for a subject."""
    subject = models.OneToOneField(
        Subject, on_delete=models.CASCADE, related_name='syllabus'
    )
    course_type = models.CharField(
        max_length=100, blank=True, default='Professional Core Course (PCC)'
    )
    course_objectives = models.TextField(
        blank=True, help_text="Course objectives (markdown or bullet list)"
    )
    course_outcomes = models.TextField(
        blank=True, help_text="Expected course outcomes after completion"
    )
    textbooks = models.TextField(
        blank=True, help_text="Prescribed textbooks with authors and editions"
    )
    reference_books = models.TextField(
        blank=True, help_text="Reference books and materials"
    )
    additional_resources = models.TextField(
        blank=True, help_text="Web links, NPTEL/Coursera, and tools"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Syllabus'
        verbose_name_plural = 'Syllabi'

    def __str__(self):
        return f"Syllabus: {self.subject.subject_code} — {self.subject.name}"


class Unit(models.Model):
    """A unit within a subject / syllabus."""
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name='units'
    )
    syllabus = models.ForeignKey(
        Syllabus, on_delete=models.CASCADE, related_name='units', null=True, blank=True
    )
    unit_number = models.PositiveSmallIntegerField()   # 1-5
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['unit_number']
        unique_together = ['subject', 'unit_number']

    def __str__(self):
        return f"Unit {self.unit_number}: {self.name} ({self.subject.subject_code})"

    def save(self, *args, **kwargs):
        if not self.syllabus_id and self.subject_id:
            syllabus, _ = Syllabus.objects.get_or_create(subject=self.subject)
            self.syllabus = syllabus
        super().save(*args, **kwargs)


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
