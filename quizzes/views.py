"""
Quiz engine views — browse, start, answer, submit, results.

Flow:
  quiz_list → quiz_detail → start_quiz → take_quiz → submit_quiz → quiz_results
"""

import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Q, Avg

from .models import Quiz, QuizQuestion, QuizAttempt, QuizAnalysis
from academics.models import Subject, Unit, Topic
from .services import analyze_attempt, generate_quiz_ai_feedback


# ────────────────────────────────────────────────
# BROWSE QUIZZES
# ────────────────────────────────────────────────

@login_required
def quiz_list(request):
    """Browse all available quizzes, filtered by student's subjects."""
    student = request.user
    quizzes = Quiz.objects.filter(is_active=True).select_related('subject', 'unit', 'topic')

    # Filter by student's current semester subjects
    subject_filter = request.GET.get('subject')
    difficulty_filter = request.GET.get('difficulty')
    type_filter = request.GET.get('type')
    search_q = request.GET.get('q', '')

    if subject_filter:
        quizzes = quizzes.filter(subject_id=subject_filter)
    if difficulty_filter:
        quizzes = quizzes.filter(difficulty=difficulty_filter)
    if type_filter:
        quizzes = quizzes.filter(quiz_type=type_filter)
    if search_q:
        quizzes = quizzes.filter(
            Q(title__icontains=search_q) | Q(subject__name__icontains=search_q)
        )

    # Get student's subjects for filter dropdown
    subjects = []
    if student.academic_info_complete:
        from academics.models import Semester
        semester = Semester.objects.filter(
            regulation=student.regulation,
            branch=student.branch,
            semester_number=student.current_semester
        ).first()
        if semester:
            subjects = list(Subject.objects.filter(semester=semester, is_active=True))

    # Get student's past attempts to show completion status
    attempted_quiz_ids = set(
        student.quiz_attempts.filter(status='completed').values_list('quiz_id', flat=True)
    )

    # Annotate each quiz with attempt status
    quizzes_with_status = []
    for quiz in quizzes:
        best_attempt = student.quiz_attempts.filter(
            quiz=quiz, status='completed'
        ).order_by('-score').first()
        quizzes_with_status.append({
            'quiz': quiz,
            'attempted': quiz.id in attempted_quiz_ids,
            'best_score': best_attempt.percentage if best_attempt else None,
            'passed': best_attempt.passed if best_attempt else False,
        })

    return render(request, 'quizzes/quiz_list.html', {
        'quizzes_with_status': quizzes_with_status,
        'subjects': subjects,
        'subject_filter': subject_filter,
        'difficulty_filter': difficulty_filter,
        'type_filter': type_filter,
        'search_q': search_q,
        'total_count': len(quizzes_with_status),
    })


@login_required
def quiz_detail(request, quiz_id):
    """Quiz landing page — show info before starting."""
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    questions = quiz.questions.all()

    # Check if student has an in-progress attempt
    in_progress = QuizAttempt.objects.filter(
        student=request.user, quiz=quiz, status='in_progress'
    ).first()

    # Past completed attempts
    past_attempts = QuizAttempt.objects.filter(
        student=request.user, quiz=quiz, status='completed'
    ).order_by('-completed_at')[:5]

    best_attempt = past_attempts.order_by('-score').first()

    return render(request, 'quizzes/quiz_detail.html', {
        'quiz': quiz,
        'question_count': questions.count(),
        'in_progress': in_progress,
        'past_attempts': past_attempts,
        'best_attempt': best_attempt,
    })


# ────────────────────────────────────────────────
# TAKE QUIZ
# ────────────────────────────────────────────────

@login_required
def start_quiz(request, quiz_id):
    """Start a new quiz attempt."""
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)

    # If there's already an in-progress attempt, resume it
    existing = QuizAttempt.objects.filter(
        student=request.user, quiz=quiz, status='in_progress'
    ).first()

    if existing:
        return redirect('quizzes:take_quiz', attempt_id=existing.id)

    # Create new attempt
    attempt = QuizAttempt.objects.create(
        student=request.user,
        quiz=quiz,
        total_questions=quiz.questions.count(),
    )

    return redirect('quizzes:take_quiz', attempt_id=attempt.id)


@login_required
def take_quiz(request, attempt_id):
    """
    The quiz-taking interface.
    All questions are loaded at once (for offline/timer support).
    JavaScript handles navigation and timer on the client side.
    """
    attempt = get_object_or_404(
        QuizAttempt, id=attempt_id, student=request.user, status='in_progress'
    )
    quiz = attempt.quiz
    questions = list(quiz.questions.all().prefetch_related('topic'))

    if not questions:
        return redirect('quizzes:quiz_detail', quiz_id=quiz.id)

    # Calculate time remaining (in seconds)
    time_limit_seconds = quiz.time_limit_minutes * 60
    elapsed = (timezone.now() - attempt.started_at).total_seconds()
    time_remaining = max(0, int(time_limit_seconds - elapsed))

    # Auto-submit if time's up
    if time_remaining <= 0:
        attempt.status = 'timed_out'
        attempt.save()
        return redirect('quizzes:quiz_results', attempt_id=attempt.id)

    # Serialize questions for JavaScript
    questions_data = []
    for i, q in enumerate(questions):
        questions_data.append({
            'id': q.id,
            'order': i + 1,
            'text': q.question_text,
            'type': q.question_type,
            'options': q.options,
            'marks': q.marks,
        })

    return render(request, 'quizzes/take_quiz.html', {
        'attempt': attempt,
        'quiz': quiz,
        'questions_data': json.dumps(questions_data),
        'time_remaining': time_remaining,
        'total_questions': len(questions),
        'saved_answers': attempt.answers,  # resume support
    })


@login_required
@require_POST
def save_answer(request, attempt_id):
    """AJAX: Save a single answer without submitting."""
    attempt = get_object_or_404(
        QuizAttempt, id=attempt_id, student=request.user, status='in_progress'
    )

    try:
        data = json.loads(request.body)
        question_id = str(data.get('question_id'))
        answer = data.get('answer', '')
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Invalid data'}, status=400)

    answers = attempt.answers or {}
    answers[question_id] = answer
    attempt.answers = answers
    attempt.save(update_fields=['answers'])

    return JsonResponse({'saved': True, 'question_id': question_id})


@login_required
@require_POST
def submit_quiz(request, attempt_id):
    """Submit quiz — score answers, generate analysis, redirect to results."""
    attempt = get_object_or_404(
        QuizAttempt, id=attempt_id, student=request.user, status='in_progress'
    )

    try:
        data = json.loads(request.body)
        final_answers = data.get('answers', {})
        time_taken = data.get('time_taken', 0)
    except json.JSONDecodeError:
        final_answers = attempt.answers or {}
        time_taken = 0

    # Save final answers
    attempt.answers = final_answers

    # Score the attempt
    questions = attempt.quiz.questions.all()
    correct_count = 0
    wrong_count = 0
    total_score = 0

    topic_results = {}  # topic_id → {correct, total}

    for question in questions:
        q_id = str(question.id)
        student_answer = final_answers.get(q_id, '').strip().upper()
        correct = question.correct_answer.strip().upper()

        is_correct = student_answer == correct

        if is_correct:
            correct_count += 1
            total_score += question.marks
        else:
            wrong_count += 1

        # Track topic-level performance
        if question.topic:
            t_id = question.topic_id
            if t_id not in topic_results:
                topic_results[t_id] = {
                    'name': question.topic.name,
                    'correct': 0,
                    'total': 0
                }
            topic_results[t_id]['total'] += 1
            if is_correct:
                topic_results[t_id]['correct'] += 1

    # Update attempt
    attempt.score = total_score
    attempt.correct_count = correct_count
    attempt.wrong_count = wrong_count
    attempt.time_taken_seconds = int(time_taken)
    attempt.status = 'completed'
    attempt.completed_at = timezone.now()
    attempt.save()

    # Generate analysis
    analyze_attempt(attempt, topic_results)

    # Record learning activity for streak
    from progress.services import record_learning_activity
    record_learning_activity(
        student=request.user,
        activity_type='quiz_submit',
        description=f'Completed quiz: {attempt.quiz.title}'
    )

    return JsonResponse({
        'success': True,
        'redirect_url': f'/quizzes/results/{attempt.id}/'
    })


# ────────────────────────────────────────────────
# RESULTS & ANALYSIS
# ────────────────────────────────────────────────

@login_required
def quiz_results(request, attempt_id):
    """Show detailed quiz results with analysis and recommendations."""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)

    if attempt.status == 'in_progress':
        return redirect('quizzes:take_quiz', attempt_id=attempt.id)

    quiz = attempt.quiz
    questions = list(quiz.questions.all().prefetch_related('topic'))

    # Build per-question result with correct answer shown
    question_results = []
    for q in questions:
        q_id = str(q.id)
        student_ans = attempt.answers.get(q_id, '')
        is_correct = student_ans.strip().upper() == q.correct_answer.strip().upper()
        question_results.append({
            'question': q,
            'student_answer': student_ans,
            'is_correct': is_correct,
            'correct_answer': q.correct_answer,
        })

    # Get or create analysis
    try:
        analysis = attempt.analysis
    except QuizAnalysis.DoesNotExist:
        analysis = None

    # Subject-level stats (for chart)
    total_marks = quiz.total_marks or 1
    score_pct = round((attempt.score / total_marks) * 100, 1)

    return render(request, 'quizzes/quiz_results.html', {
        'attempt': attempt,
        'quiz': quiz,
        'question_results': question_results,
        'analysis': analysis,
        'score_pct': score_pct,
        'time_taken_fmt': _format_time(attempt.time_taken_seconds),
    })


@login_required
def my_attempts(request):
    """Student's quiz attempt history."""
    attempts = QuizAttempt.objects.filter(
        student=request.user, status='completed'
    ).select_related('quiz', 'quiz__subject').order_by('-completed_at')

    avg_score = attempts.aggregate(avg=Avg('score'))['avg'] or 0

    return render(request, 'quizzes/my_attempts.html', {
        'attempts': attempts,
        'avg_score': round(avg_score, 1),
        'total_count': attempts.count(),
    })


def _format_time(seconds):
    """Convert seconds to mm:ss string."""
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m}m {s:02d}s"
