from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from .models import QuestionPaper, PYQQuestion
from academics.models import Subject, Unit, Topic

@login_required
def paper_list(request):
    papers = QuestionPaper.objects.filter(is_verified=True).select_related('subject')
    subject = request.GET.get('subject')
    year = request.GET.get('year')
    exam_type = request.GET.get('exam_type')
    if subject: papers = papers.filter(subject_id=subject)
    if year: papers = papers.filter(year=year)
    if exam_type: papers = papers.filter(exam_type=exam_type)
    subjects = Subject.objects.filter(is_active=True)
    years = QuestionPaper.objects.filter(is_verified=True).values_list('year', flat=True).distinct().order_by('-year')
    return render(request, 'pyqs/paper_list.html', {'papers': papers, 'subjects': subjects, 'years': years, 'exam_types': QuestionPaper.EXAM_TYPES})

@login_required
def important_questions(request):
    questions = PYQQuestion.objects.filter(paper__is_verified=True).select_related('paper','paper__subject','unit','topic').order_by('-importance_score')
    subject = request.GET.get('subject')
    unit = request.GET.get('unit')
    if subject: questions = questions.filter(paper__subject_id=subject)
    if unit: questions = questions.filter(unit_id=unit)
    subjects = Subject.objects.filter(is_active=True)
    units = Unit.objects.all()
    return render(request, 'pyqs/important.html', {'questions': questions, 'subjects': subjects, 'units': units})

@login_required
def paper_detail(request, paper_id):
    paper = get_object_or_404(QuestionPaper, id=paper_id, is_verified=True)
    questions = paper.questions.select_related('unit','topic').all()
    return render(request, 'pyqs/paper_detail.html', {'paper': paper, 'questions': questions})

@login_required
def question_detail(request, question_id):
    question = get_object_or_404(PYQQuestion.objects.select_related('paper','paper__subject','unit','topic'), id=question_id, paper__is_verified=True)
    return render(request, 'pyqs/question_detail.html', {'question': question})
