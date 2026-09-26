"""Dashboard views — Student personalized home."""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from academics.models import Semester, Subject


@login_required
def dashboard_home(request):
    """Main student dashboard."""
    student = request.user

    if not student.academic_info_complete:
        return redirect('accounts:setup_profile')

    # Get student's current semester subjects
    subjects = []
    semester = None

    if student.regulation and student.branch and student.current_semester:
        semester = Semester.objects.filter(
            regulation=student.regulation,
            branch=student.branch,
            semester_number=student.current_semester
        ).first()
        if semester:
            subjects = list(Subject.objects.filter(
                semester=semester, is_active=True
            ).prefetch_related('units'))

    # Stats
    quiz_attempts = student.quiz_attempts.filter(status='completed')
    total_quizzes = quiz_attempts.count()
    avg_score = 0
    if total_quizzes > 0:
        avg_score = round(
            sum(a.percentage for a in quiz_attempts) / total_quizzes, 1
        )

    # Real streak tracking info
    from progress.services import get_student_streak_info
    streak_info = get_student_streak_info(student)

    # Topics studied count
    topics_completed = student.learning_activities.filter(activity_type='topic_study').count()

    recent_chats = student.chat_sessions.all()[:3]
    recent_scans = student.scanned_questions.all()[:3]

    context = {
        'student': student,
        'semester': semester,
        'subjects': subjects,
        'total_quizzes': total_quizzes,
        'avg_score': avg_score,
        'recent_chats': recent_chats,
        'recent_scans': recent_scans,
        'questions_asked': student.total_questions_asked,
        'streak_info': streak_info,
        'topics_completed': topics_completed,
    }

    return render(request, 'dashboard/home.html', context)
