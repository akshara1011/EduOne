"""
Views for academic hierarchy — syllabus, subjects, units, topics.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import University, Regulation, Branch, Semester, Subject, Unit, Topic


@login_required
def syllabus_home(request):
    """Show student's syllabus based on their profile."""
    student = request.user

    if not student.academic_info_complete:
        return redirect('accounts:setup_profile')

    # Get subjects for this student's semester
    semester = Semester.objects.filter(
        regulation=student.regulation,
        branch=student.branch,
        semester_number=student.current_semester
    ).first()

    subjects = []
    if semester:
        subjects = Subject.objects.filter(
            semester=semester, is_active=True
        ).prefetch_related('units__topics')

    return render(request, 'academics/syllabus.html', {
        'student': student,
        'semester': semester,
        'subjects': subjects,
    })


@login_required
def subject_detail(request, subject_id):
    """Show subject overview with units, notes, videos, PYQs."""
    subject = get_object_or_404(Subject, id=subject_id, is_active=True)
    units = Unit.objects.filter(subject=subject).prefetch_related('topics')

    # Get counts for quick stats
    from resources.models import Note, Video
    from pyqs.models import QuestionPaper

    notes_count = Note.objects.filter(subject=subject, is_approved=True).count()
    videos_count = Video.objects.filter(subject=subject, is_verified=True).count()
    pyqs_count = QuestionPaper.objects.filter(subject=subject, is_verified=True).count()

    return render(request, 'academics/subject_detail.html', {
        'subject': subject,
        'units': units,
        'notes_count': notes_count,
        'videos_count': videos_count,
        'pyqs_count': pyqs_count,
    })


@login_required
def unit_detail(request, unit_id):
    """Show unit overview with topics and resources."""
    unit = get_object_or_404(Unit, id=unit_id)
    topics = Topic.objects.filter(unit=unit)

    from resources.models import Note, Video
    notes = Note.objects.filter(unit=unit, is_approved=True)[:5]
    videos = Video.objects.filter(unit=unit, is_verified=True)[:5]

    return render(request, 'academics/unit_detail.html', {
        'unit': unit,
        'topics': topics,
        'notes': notes,
        'videos': videos,
    })


@login_required
def topic_detail(request, topic_id):
    """Show topic with all resources."""
    topic = get_object_or_404(Topic, id=topic_id)

    from resources.models import Note, Video
    from pyqs.models import PYQQuestion
    from quizzes.models import Quiz

    notes = Note.objects.filter(topic=topic, is_approved=True)
    videos = Video.objects.filter(topic=topic, is_verified=True)
    pyqs = PYQQuestion.objects.filter(topic=topic).order_by('-importance_score')[:10]
    quizzes = Quiz.objects.filter(topic=topic, is_active=True)[:3]

    # Record learning activity for streak
    from progress.services import record_learning_activity
    record_learning_activity(
        student=request.user,
        activity_type='topic_study',
        description=f'Studied topic: {topic.name}'
    )

    return render(request, 'academics/topic_detail.html', {
        'topic': topic,
        'notes': notes,
        'videos': videos,
        'pyqs': pyqs,
        'quizzes': quizzes,
    })


@login_required
def subject_list(request):
    """Browse all subjects."""
    student = request.user
    subjects = Subject.objects.filter(is_active=True)

    # Filter by student's semester if profile complete
    if student.academic_info_complete:
        semester = Semester.objects.filter(
            regulation=student.regulation,
            branch=student.branch,
            semester_number=student.current_semester
        ).first()
        if semester:
            subjects = subjects.filter(semester=semester)

    return render(request, 'academics/subject_list.html', {'subjects': subjects})


@login_required
def subject_syllabus(request, subject_id):
    """Full syllabus for a single subject."""
    subject = get_object_or_404(Subject, id=subject_id)
    units = Unit.objects.filter(subject=subject).prefetch_related('topics')
    return render(request, 'academics/subject_syllabus.html', {
        'subject': subject,
        'units': units,
    })


# ──────────────────────────────────────────
# AJAX views for cascading dropdowns
# ──────────────────────────────────────────

def ajax_regulations(request):
    """Return regulations for a given university."""
    university_id = request.GET.get('university_id')
    regulations = Regulation.objects.filter(
        university_id=university_id, is_active=True
    ).values('id', 'name')
    return JsonResponse(list(regulations), safe=False)


def ajax_branches(request):
    """Return branches available for a regulation."""
    regulation_id = request.GET.get('regulation_id')
    # Branches that have semesters in this regulation
    branch_ids = Semester.objects.filter(
        regulation_id=regulation_id
    ).values_list('branch_id', flat=True).distinct()
    branches = Branch.objects.filter(id__in=branch_ids).values('id', 'name', 'short_name')
    return JsonResponse(list(branches), safe=False)


def ajax_semesters(request):
    """Return semesters for a regulation + branch."""
    regulation_id = request.GET.get('regulation_id')
    branch_id = request.GET.get('branch_id')
    semesters = Semester.objects.filter(
        regulation_id=regulation_id,
        branch_id=branch_id
    ).values('id', 'semester_number', 'year_of_study')
    return JsonResponse(list(semesters), safe=False)


def ajax_subjects(request):
    """Return subjects for a semester."""
    semester_id = request.GET.get('semester_id')
    subjects = Subject.objects.filter(
        semester_id=semester_id, is_active=True
    ).values('id', 'name', 'subject_code')
    return JsonResponse(list(subjects), safe=False)
