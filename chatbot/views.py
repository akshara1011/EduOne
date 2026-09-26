"""
Chatbot views — AI Academic Assistant.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
import json

from .models import ChatSession, ChatMessage
from .gemini_service import get_ai_response
from academics.models import Subject, Topic


@login_required
def chat_home(request):
    """Main chatbot page — creates or lists sessions."""
    student = request.user
    sessions = ChatSession.objects.filter(student=student)[:10]

    # Get student's subjects for context selector
    subjects = []
    if student.academic_info_complete:
        from academics.models import Semester
        semester = Semester.objects.filter(
            regulation=student.regulation,
            branch=student.branch,
            semester_number=student.current_semester
        ).first()
        if semester:
            subjects = list(semester.subjects.filter(is_active=True))

    return render(request, 'chatbot/chat_home.html', {
        'sessions': sessions,
        'subjects': subjects,
    })


@login_required
def new_chat(request):
    """Start a new chat session."""
    subject_id = request.GET.get('subject')
    topic_id = request.GET.get('topic')

    subject = None
    topic = None

    if subject_id:
        subject = Subject.objects.filter(id=subject_id).first()
    if topic_id:
        topic = Topic.objects.filter(id=topic_id).first()

    session = ChatSession.objects.create(
        student=request.user,
        subject=subject,
        topic=topic,
        title=f"Chat about {subject.name if subject else 'ErVeda AI'}"
    )
    return redirect('chatbot:session', session_id=session.id)


@login_required
def chat_session(request, session_id):
    """View a chat session and send messages."""
    session = get_object_or_404(ChatSession, id=session_id, student=request.user)
    messages = session.messages.all()

    # Get student's subjects for context selector
    subjects = []
    if request.user.academic_info_complete:
        from academics.models import Semester
        semester = Semester.objects.filter(
            regulation=request.user.regulation,
            branch=request.user.branch,
            semester_number=request.user.current_semester
        ).first()
        if semester:
            subjects = list(semester.subjects.filter(is_active=True))

    return render(request, 'chatbot/chat_session.html', {
        'session': session,
        'messages': messages,
        'subjects': subjects,
    })


@login_required
@require_POST
def send_message(request, session_id):
    """AJAX endpoint — send message and get AI response."""
    session = get_object_or_404(ChatSession, id=session_id, student=request.user)

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
    except json.JSONDecodeError:
        user_message = request.POST.get('message', '').strip()

    if not user_message:
        return JsonResponse({'error': 'Empty message'}, status=400)

    # Save user message
    ChatMessage.objects.create(
        session=session,
        role='user',
        content=user_message
    )

    # Auto-set session title from first message
    if not session.title or session.title.startswith('Chat about'):
        session.title = user_message[:80]
        session.save()

    # Get AI response
    ai_result = get_ai_response(
        user_message=user_message,
        session=session,
        student=request.user,
        subject=session.subject,
        topic=session.topic
    )

    # Save AI response
    ai_msg = ChatMessage.objects.create(
        session=session,
        role='assistant',
        content=ai_result['answer'],
        sources=ai_result.get('sources', [])
    )

    # Update student question count
    request.user.total_questions_asked += 1
    request.user.save(update_fields=['total_questions_asked'])

    # Record learning activity for streak
    from progress.services import record_learning_activity
    record_learning_activity(
        student=request.user,
        activity_type='ai_question',
        description=f'Asked AI: {user_message[:50]}'
    )

    return JsonResponse({
        'answer': ai_result['answer'],
        'message_id': ai_msg.id,
        'sources': ai_result.get('sources', [])
    })
