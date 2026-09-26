"""
Quiz analysis service — scores attempt, identifies weak topics,
generates AI-powered feedback using Gemini.
"""

from .models import QuizAnalysis


def analyze_attempt(attempt, topic_results: dict) -> QuizAnalysis:
    """
    Build QuizAnalysis for a completed attempt.

    Args:
        attempt: QuizAttempt instance (already scored)
        topic_results: dict of {topic_id: {'name': str, 'correct': int, 'total': int}}

    Returns:
        QuizAnalysis instance
    """
    weak_topics = []
    strong_topics = []
    recommendations = []

    for topic_id, data in topic_results.items():
        if data['total'] == 0:
            continue
        pct = (data['correct'] / data['total']) * 100

        if pct < 50:
            weak_topics.append(data['name'])
            recommendations.append(
                f"Revise '{data['name']}' — you scored {pct:.0f}% ({data['correct']}/{data['total']})"
            )
        elif pct >= 80:
            strong_topics.append(data['name'])

    # Overall performance recommendations
    score_pct = attempt.percentage
    if score_pct < 40:
        recommendations.insert(0, "Re-read all unit notes before attempting this quiz again.")
        recommendations.append("Try topic-wise quizzes to build confidence in individual topics.")
    elif score_pct < 70:
        recommendations.insert(0, "Good effort! Focus on the weak topics listed below.")
        recommendations.append("Practice PYQ questions on your weak topics for exam readiness.")
    else:
        recommendations.insert(0, "Excellent performance! You're well-prepared.")
        recommendations.append("Try a harder difficulty level or a full mock test.")

    # Generate AI feedback (sync call using Gemini)
    ai_feedback = _generate_feedback(attempt, weak_topics, strong_topics, score_pct)

    # Delete existing analysis if re-attempting
    QuizAnalysis.objects.filter(attempt=attempt).delete()

    analysis = QuizAnalysis.objects.create(
        attempt=attempt,
        weak_topics=weak_topics,
        strong_topics=strong_topics,
        recommendations=recommendations,
        ai_feedback=ai_feedback,
    )

    return analysis


def _generate_feedback(attempt, weak_topics, strong_topics, score_pct) -> str:
    """Generate short AI feedback for the quiz result."""
    from django.conf import settings

    if not settings.GEMINI_API_KEY:
        # Fallback rule-based feedback
        if score_pct >= 80:
            return f"Outstanding! You scored {score_pct}% on {attempt.quiz.title}. Keep up this preparation level before the exam."
        elif score_pct >= 60:
            return f"Good attempt! You scored {score_pct}%. Focus on improving: {', '.join(weak_topics[:3]) or 'the missed questions'}."
        else:
            return f"You scored {score_pct}% on {attempt.quiz.title}. Don't be discouraged — revisit the notes and try again. Topics to focus on: {', '.join(weak_topics[:3]) or 'all units'}."

    try:
        from chatbot.gemini_service import generate_ai_text

        prompt = (
            f"A B.Tech student just completed a quiz: '{attempt.quiz.title}' "
            f"(Subject: {attempt.quiz.subject.name}).\n"
            f"Score: {score_pct}% ({attempt.correct_count} correct, {attempt.wrong_count} wrong).\n"
            f"Weak topics: {', '.join(weak_topics) or 'None'}.\n"
            f"Strong topics: {', '.join(strong_topics) or 'None'}.\n\n"
            "Write a 2-3 sentence encouraging and actionable feedback message for this student. "
            "Be specific, motivating, and exam-focused. Keep it under 60 words."
        )

        response_text = generate_ai_text(prompt)
        if response_text:
            return response_text.strip()
        return f"You scored {score_pct}%. {'Great job!' if score_pct >= 70 else 'Keep practicing!'} Review your weak topics and attempt again."

    except Exception:
        return f"You scored {score_pct}%. {'Great job!' if score_pct >= 70 else 'Keep practicing!'} Review your weak topics and attempt again."



def generate_quiz_ai_feedback(quiz, subject_name, score_pct, weak_topics):
    """Public helper — kept for external callers."""
    return _generate_feedback(None, weak_topics, [], score_pct)
