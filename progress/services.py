"""
Learning Activity and Streak Engine for ErVeda.

Calculates real calendar-day streaks according to configured Django timezone (Asia/Kolkata).
One meaningful activity per calendar day sustains the streak.
"""

import datetime
from django.utils import timezone
from .models import LearningActivity


def calculate_streak(student):
    """
    Calculate real calendar-day streak for a student using configured timezone.

    Returns dict:
        current_streak: int
        longest_streak: int
        has_activity_today: bool
        is_first_time: bool
        total_active_days: int
    """
    tz = timezone.get_current_timezone()
    now_local = timezone.localtime(timezone.now(), tz)
    today = now_local.date()
    yesterday = today - datetime.timedelta(days=1)

    # Fetch all activity timestamps for the student
    activity_timestamps = student.learning_activities.values_list('created_at', flat=True)

    if not activity_timestamps:
        return {
            'current_streak': 0,
            'longest_streak': 0,
            'has_activity_today': False,
            'is_first_time': True,
            'total_active_days': 0,
        }

    # Convert all activity timestamps to unique local calendar dates
    unique_dates = sorted(set(
        timezone.localtime(ts, tz).date() for ts in activity_timestamps
    ))

    total_active_days = len(unique_dates)
    has_activity_today = today in unique_dates
    has_activity_yesterday = yesterday in unique_dates

    # Calculate longest streak across entire history
    longest_streak = 0
    if unique_dates:
        longest_streak = 1
        current_run = 1
        for i in range(1, len(unique_dates)):
            if unique_dates[i] == unique_dates[i - 1] + datetime.timedelta(days=1):
                current_run += 1
                if current_run > longest_streak:
                    longest_streak = current_run
            else:
                current_run = 1

    # Calculate current streak
    date_set = set(unique_dates)
    current_streak = 0

    if has_activity_today:
        current_streak = 1
        check_date = today - datetime.timedelta(days=1)
        while check_date in date_set:
            current_streak += 1
            check_date -= datetime.timedelta(days=1)
    elif has_activity_yesterday:
        # User hasn't learned yet today, but streak from yesterday is still alive!
        current_streak = 1
        check_date = yesterday - datetime.timedelta(days=1)
        while check_date in date_set:
            current_streak += 1
            check_date -= datetime.timedelta(days=1)
    else:
        # Missed at least 2 consecutive calendar days
        current_streak = 0

    return {
        'current_streak': current_streak,
        'longest_streak': max(longest_streak, current_streak),
        'has_activity_today': has_activity_today,
        'is_first_time': False,
        'total_active_days': total_active_days,
    }


def record_learning_activity(student, activity_type, description=''):
    """
    Records a meaningful learning activity and updates the student's streak in the database.
    """
    activity = LearningActivity.objects.create(
        student=student,
        activity_type=activity_type,
        description=description
    )

    streak_info = calculate_streak(student)

    # Update Student model fields
    update_fields = []
    if student.study_streak != streak_info['current_streak']:
        student.study_streak = streak_info['current_streak']
        update_fields.append('study_streak')

    if student.longest_streak < streak_info['longest_streak']:
        student.longest_streak = streak_info['longest_streak']
        update_fields.append('longest_streak')

    if update_fields:
        student.save(update_fields=update_fields)

    return activity, streak_info


def get_student_streak_info(student):
    """
    Helper to fetch streak info for views and templates.
    """
    if not student or not student.is_authenticated:
        return {
            'current_streak': 0,
            'longest_streak': 0,
            'has_activity_today': False,
            'is_first_time': True,
            'total_active_days': 0,
        }
    return calculate_streak(student)


def backfill_historical_activities():
    """
    Backfill LearningActivity records from existing QuizAttempts, ChatMessages, and ScannedQuestions.
    """
    from accounts.models import Student
    from quizzes.models import QuizAttempt
    from chatbot.models import ChatMessage
    from question_solver.models import ScannedQuestion

    created_count = 0
    for student in Student.objects.all():
        # Completed quiz attempts
        for attempt in QuizAttempt.objects.filter(student=student, status='completed'):
            dt = attempt.completed_at or attempt.started_at
            if dt and not LearningActivity.objects.filter(student=student, activity_type='quiz_submit', created_at=dt).exists():
                act = LearningActivity.objects.create(
                    student=student,
                    activity_type='quiz_submit',
                    description=f'Quiz completed: {attempt.quiz.title}'
                )
                LearningActivity.objects.filter(id=act.id).update(created_at=dt)
                created_count += 1

        # Chat messages from user
        for msg in ChatMessage.objects.filter(session__student=student, role='user'):
            if not LearningActivity.objects.filter(student=student, activity_type='ai_question', created_at=msg.created_at).exists():
                act = LearningActivity.objects.create(
                    student=student,
                    activity_type='ai_question',
                    description='Asked AI Tutor a question'
                )
                LearningActivity.objects.filter(id=act.id).update(created_at=msg.created_at)
                created_count += 1

        # Scanned questions
        for scan in ScannedQuestion.objects.filter(student=student):
            if not LearningActivity.objects.filter(student=student, activity_type='scan_question', created_at=scan.created_at).exists():
                act = LearningActivity.objects.create(
                    student=student,
                    activity_type='scan_question',
                    description='Scanned a question'
                )
                LearningActivity.objects.filter(id=act.id).update(created_at=scan.created_at)
                created_count += 1

        # Recalculate streak for this student
        streak_info = calculate_streak(student)
        student.study_streak = streak_info['current_streak']
        student.longest_streak = streak_info['longest_streak']
        student.save(update_fields=['study_streak', 'longest_streak'])

    return created_count
