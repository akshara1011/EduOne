from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .models import Note, Video
from academics.models import Subject, Unit, Topic


# ============================================================
# RESOURCES HOME
# ============================================================

def resources_home(request):
    """
    Resources visual learning library.
    Shows categorized hubs: Notes, Video Lectures, PYQs, and Quizzes.
    """
    from pyqs.models import QuestionPaper, PYQQuestion
    from quizzes.models import Quiz

    notes_count = Note.objects.filter(is_approved=True).count()
    videos_count = Video.objects.filter(is_verified=True).count()
    pyqs_count = QuestionPaper.objects.filter(is_verified=True).count()
    quizzes_count = Quiz.objects.filter(is_active=True).count()

    recent_notes = Note.objects.filter(is_approved=True).select_related('subject', 'unit', 'topic')[:6]
    recent_videos = Video.objects.filter(is_verified=True).select_related('subject', 'unit', 'topic')[:4]
    subjects = Subject.objects.filter(is_active=True)[:8]

    context = {
        'notes_count': notes_count,
        'videos_count': videos_count,
        'pyqs_count': pyqs_count,
        'quizzes_count': quizzes_count,
        'recent_notes': recent_notes,
        'recent_videos': recent_videos,
        'subjects': subjects,
    }

    return render(request, "resources/home.html", context)


# ============================================================
# FILTER HELPER
# ============================================================

def _apply_filters(queryset, request):
    """
    Apply subject, unit, topic and search filters
    to Notes/Videos querysets.
    """

    subject = request.GET.get("subject")
    unit = request.GET.get("unit")
    topic = request.GET.get("topic")
    search_query = request.GET.get("q", "").strip()

    if subject:
        queryset = queryset.filter(subject_id=subject)

    if unit:
        queryset = queryset.filter(unit_id=unit)

    if topic:
        queryset = queryset.filter(topic_id=topic)

    if search_query:
        queryset = queryset.filter(
            title__icontains=search_query
        )

    return queryset


# ============================================================
# NOTES
# ============================================================

@login_required
def notes(request):
    """
    Display approved study notes.

    Supports filtering by:
    - Subject
    - Unit
    - Topic
    - Search keyword
    """

    notes_qs = (
        Note.objects
        .filter(is_approved=True)
        .select_related("subject", "unit", "topic")
    )

    notes_qs = _apply_filters(notes_qs, request)

    subjects = Subject.objects.filter(is_active=True)
    units = Unit.objects.all()
    topics = Topic.objects.all()

    context = {
        "notes": notes_qs,
        "subjects": subjects,
        "units": units,
        "topics": topics,
        "filters": request.GET,
    }

    return render(
        request,
        "resources/notes.html",
        context
    )


# ============================================================
# VIDEOS
# ============================================================

@login_required
def videos(request):
    """
    Display verified educational videos.

    Supports filtering by:
    - Subject
    - Unit
    - Topic
    - Difficulty
    - Search keyword
    """

    videos_qs = (
        Video.objects
        .filter(is_verified=True)
        .select_related("subject", "unit", "topic")
    )

    videos_qs = _apply_filters(videos_qs, request)

    difficulty = request.GET.get("difficulty")

    if difficulty:
        videos_qs = videos_qs.filter(
            difficulty=difficulty
        )

    subjects = Subject.objects.filter(is_active=True)
    units = Unit.objects.all()
    topics = Topic.objects.all()

    context = {
        "videos": videos_qs,
        "subjects": subjects,
        "units": units,
        "topics": topics,
        "filters": request.GET,
    }

    return render(
        request,
        "resources/videos.html",
        context
    )


# ============================================================
# DOWNLOAD NOTE
# ============================================================

@login_required
def download_note(request, note_id):
    """
    Download an approved PDF note.

    Also increases the download counter.
    """

    note = get_object_or_404(
        Note,
        id=note_id,
        is_approved=True
    )

    # Make sure the note actually has a PDF
    if not note.pdf_file:
        return redirect("resources:notes")

    # Increase download count
    Note.objects.filter(
        pk=note.pk
    ).update(
        download_count=note.download_count + 1
    )

    # Record learning activity for streak
    from progress.services import record_learning_activity
    record_learning_activity(
        student=request.user,
        activity_type='note_view',
        description=f'Studied note: {note.title}'
    )

    # Redirect to the uploaded PDF
    return redirect(note.pdf_file.url)