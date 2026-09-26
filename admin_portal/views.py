"""
Centralized Admin Portal Views for ErVeda.
Provides comprehensive web-based management for Students, Academics, Resources, PYQs, and Quizzes.
"""
from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.core.paginator import Paginator
from django.db.models import Count, Q

from academics.models import University, Regulation, Branch, Semester, Subject, Unit, Topic
from resources.models import Note, Video
from pyqs.models import QuestionPaper, PYQQuestion
from quizzes.models import Quiz, QuizQuestion, QuizAttempt
from chatbot.models import ChatSession
from question_solver.models import ScannedQuestion

from .forms import (
    AdminLoginForm, AdminStudentForm, UniversityForm, RegulationForm,
    BranchForm, SemesterForm, SubjectForm, UnitForm, TopicForm,
    NoteForm, VideoForm, QuestionPaperForm, PYQQuestionForm,
    QuizForm, QuizQuestionForm
)

Student = get_user_model()


def admin_required(view_func):
    """Decorator ensuring that only authenticated staff/superusers can access admin portal views."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin_portal:login')
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "Access denied. Only authorized staff and administrators can access the Admin Portal.")
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# ══════════════════════════════════════════════════════════════════
# AUTHENTICATION
# ══════════════════════════════════════════════════════════════════

def admin_login(request):
    """Dedicated admin portal login."""
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('admin_portal:dashboard')

    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user, backend='accounts.backends.EmailOrUsernameModelBackend')
            messages.success(request, f"Welcome to the Admin Portal, {user.display_name}!")
            return redirect('admin_portal:dashboard')
    else:
        form = AdminLoginForm()

    return render(request, 'admin_portal/login.html', {'form': form})


def admin_logout(request):
    """Admin logout view."""
    logout(request)
    messages.info(request, "You have been logged out from the Admin Portal.")
    return redirect('admin_portal:login')


# ══════════════════════════════════════════════════════════════════
# CENTRALIZED DASHBOARD
# ══════════════════════════════════════════════════════════════════

@admin_required
def dashboard(request):
    """Centralized administrative dashboard."""
    # Key Metrics
    total_students = Student.objects.count()
    active_students = Student.objects.filter(is_active=True).count()
    staff_count = Student.objects.filter(is_staff=True).count()

    total_universities = University.objects.count()
    total_regulations = Regulation.objects.count()
    total_branches = Branch.objects.count()
    total_subjects = Subject.objects.count()
    total_units = Unit.objects.count()

    total_notes = Note.objects.count()
    approved_notes = Note.objects.filter(is_approved=True).count()
    pending_notes = Note.objects.filter(is_approved=False).count()
    total_videos = Video.objects.count()

    total_papers = QuestionPaper.objects.count()
    total_pyq_questions = PYQQuestion.objects.count()

    total_quizzes = Quiz.objects.count()
    total_attempts = QuizAttempt.objects.count()

    total_chat_sessions = ChatSession.objects.count()
    total_scans = ScannedQuestion.objects.count()

    # Recent Records
    recent_students = Student.objects.select_related('university', 'branch').order_by('-created_at')[:6]
    recent_notes = Note.objects.select_related('subject', 'uploaded_by').order_by('-created_at')[:5]
    recent_papers = QuestionPaper.objects.select_related('subject').order_by('-created_at')[:5]

    # University Breakdown
    univ_stats = University.objects.annotate(
        reg_count=Count('regulations', distinct=True),
        student_count=Count('students', distinct=True)
    )

    context = {
        'total_students': total_students,
        'active_students': active_students,
        'staff_count': staff_count,
        'total_universities': total_universities,
        'total_regulations': total_regulations,
        'total_branches': total_branches,
        'total_subjects': total_subjects,
        'total_units': total_units,
        'total_notes': total_notes,
        'approved_notes': approved_notes,
        'pending_notes': pending_notes,
        'total_videos': total_videos,
        'total_papers': total_papers,
        'total_pyq_questions': total_pyq_questions,
        'total_quizzes': total_quizzes,
        'total_attempts': total_attempts,
        'total_chat_sessions': total_chat_sessions,
        'total_scans': total_scans,
        'recent_students': recent_students,
        'recent_notes': recent_notes,
        'recent_papers': recent_papers,
        'univ_stats': univ_stats,
    }
    return render(request, 'admin_portal/dashboard.html', context)


# ══════════════════════════════════════════════════════════════════
# STUDENTS MANAGEMENT
# ══════════════════════════════════════════════════════════════════

@admin_required
def student_list(request):
    """List, search, and filter students."""
    query = request.GET.get('q', '').strip()
    branch_id = request.GET.get('branch', '')
    univ_id = request.GET.get('university', '')
    status_filter = request.GET.get('status', '')

    students = Student.objects.select_related('university', 'branch', 'regulation').order_by('-created_at')

    if query:
        students = students.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(college_name__icontains=query)
        )
    if branch_id:
        students = students.filter(branch_id=branch_id)
    if univ_id:
        students = students.filter(university_id=univ_id)
    if status_filter == 'active':
        students = students.filter(is_active=True)
    elif status_filter == 'inactive':
        students = students.filter(is_active=False)
    elif status_filter == 'staff':
        students = students.filter(is_staff=True)

    paginator = Paginator(students, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    universities = University.objects.filter(is_active=True)
    branches = Branch.objects.filter(is_active=True)

    return render(request, 'admin_portal/students/list.html', {
        'page_obj': page_obj,
        'query': query,
        'branch_id': branch_id,
        'univ_id': univ_id,
        'status_filter': status_filter,
        'universities': universities,
        'branches': branches,
        'total_count': paginator.count,
    })


@admin_required
def student_detail(request, student_id):
    """Detailed view of a student account and activity."""
    student = get_object_or_404(Student.objects.select_related('university', 'regulation', 'branch'), pk=student_id)
    quiz_attempts = student.quiz_attempts.select_related('quiz').order_by('-id')[:8]
    chat_sessions = student.chat_sessions.select_related('subject').order_by('-last_activity')[:8]
    uploaded_notes = student.uploaded_notes.select_related('subject').order_by('-created_at')[:5]

    return render(request, 'admin_portal/students/detail.html', {
        'student': student,
        'quiz_attempts': quiz_attempts,
        'chat_sessions': chat_sessions,
        'uploaded_notes': uploaded_notes,
    })


@admin_required
def student_create(request):
    """Create a new student or admin account."""
    if request.method == 'POST':
        form = AdminStudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"Student '{student.display_name}' created successfully.")
            return redirect('admin_portal:student_detail', student_id=student.id)
    else:
        form = AdminStudentForm()

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': 'Add New Student / Staff Account',
        'subtitle': 'Create a student profile or grant administrative staff privileges.',
        'cancel_url': 'admin_portal:student_list',
        'submit_text': 'Create Account',
    })


@admin_required
def student_edit(request, student_id):
    """Edit student details."""
    student = get_object_or_404(Student, pk=student_id)
    if request.method == 'POST':
        form = AdminStudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f"Student profile '{student.display_name}' updated successfully.")
            return redirect('admin_portal:student_detail', student_id=student.id)
    else:
        form = AdminStudentForm(instance=student)

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': f"Edit Student: {student.display_name}",
        'subtitle': f"Modify academic enrollment, contact info, or account permissions.",
        'cancel_url': 'admin_portal:student_list',
        'submit_text': 'Save Changes',
    })


@admin_required
def student_delete(request, student_id):
    """Delete a student account."""
    student = get_object_or_404(Student, pk=student_id)
    if student.id == request.user.id:
        messages.error(request, "You cannot delete your own logged-in admin account!")
        return redirect('admin_portal:student_list')

    if request.method == 'POST':
        name = student.display_name
        student.delete()
        messages.success(request, f"Student account '{name}' has been permanently deleted.")
        return redirect('admin_portal:student_list')

    return render(request, 'admin_portal/confirm_delete.html', {
        'object_name': f"Student: {student.display_name} ({student.email})",
        'warning_text': "Deleting this student will also delete their quiz attempts, notes uploaded, and learning activity.",
        'cancel_url': 'admin_portal:student_list',
    })


@admin_required
def student_toggle_status(request, student_id):
    """Quick toggle student active status."""
    student = get_object_or_404(Student, pk=student_id)
    if student.id == request.user.id:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect('admin_portal:student_list')

    student.is_active = not student.is_active
    student.save()
    status_str = "activated" if student.is_active else "deactivated"
    messages.success(request, f"Student '{student.display_name}' has been {status_str}.")
    return redirect('admin_portal:student_list')


# ══════════════════════════════════════════════════════════════════
# ACADEMICS: UNIVERSITIES
# ══════════════════════════════════════════════════════════════════

@admin_required
def university_list(request):
    universities = University.objects.annotate(
        reg_count=Count('regulations', distinct=True),
        student_count=Count('students', distinct=True)
    ).order_by('name')
    return render(request, 'admin_portal/academics/university_list.html', {'universities': universities})


@admin_required
def university_create(request):
    if request.method == 'POST':
        form = UniversityForm(request.POST, request.FILES)
        if form.is_valid():
            u = form.save()
            messages.success(request, f"University '{u.short_name}' created successfully.")
            return redirect('admin_portal:university_list')
    else:
        form = UniversityForm()

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': 'Add New University',
        'subtitle': 'Add an accredited technical institution to the syllabus hierarchy.',
        'cancel_url': 'admin_portal:university_list',
        'submit_text': 'Save University',
    })


@admin_required
def university_edit(request, pk):
    university = get_object_or_404(University, pk=pk)
    if request.method == 'POST':
        form = UniversityForm(request.POST, request.FILES, instance=university)
        if form.is_valid():
            u = form.save()
            messages.success(request, f"University '{u.short_name}' updated successfully.")
            return redirect('admin_portal:university_list')
    else:
        form = UniversityForm(instance=university)

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': f"Edit University: {university.short_name}",
        'subtitle': 'Update institution name, state, logo, or website URL.',
        'cancel_url': 'admin_portal:university_list',
        'submit_text': 'Save Changes',
    })


@admin_required
def university_delete(request, pk):
    university = get_object_or_404(University, pk=pk)
    if request.method == 'POST':
        name = university.short_name
        university.delete()
        messages.success(request, f"University '{name}' deleted successfully.")
        return redirect('admin_portal:university_list')

    return render(request, 'admin_portal/confirm_delete.html', {
        'object_name': f"University: {university.name} ({university.short_name})",
        'warning_text': "Deleting this university will cascade delete all linked regulations, semesters, and subjects!",
        'cancel_url': 'admin_portal:university_list',
    })


# ══════════════════════════════════════════════════════════════════
# ACADEMICS: REGULATIONS
# ══════════════════════════════════════════════════════════════════

@admin_required
def regulation_list(request):
    regulations = Regulation.objects.select_related('university').annotate(
        sem_count=Count('semesters', distinct=True)
    ).order_by('university__short_name', '-year')
    return render(request, 'admin_portal/academics/regulation_list.html', {'regulations': regulations})


@admin_required
def regulation_create(request):
    if request.method == 'POST':
        form = RegulationForm(request.POST)
        if form.is_valid():
            r = form.save()
            messages.success(request, f"Regulation '{r}' created successfully.")
            return redirect('admin_portal:regulation_list')
    else:
        form = RegulationForm()

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': 'Add Academic Regulation',
        'subtitle': 'e.g. JNTUH R22, VTU 2021 Scheme, AKTU NEP Scheme.',
        'cancel_url': 'admin_portal:regulation_list',
        'submit_text': 'Save Regulation',
    })


@admin_required
def regulation_edit(request, pk):
    reg = get_object_or_404(Regulation, pk=pk)
    if request.method == 'POST':
        form = RegulationForm(request.POST, instance=reg)
        if form.is_valid():
            r = form.save()
            messages.success(request, f"Regulation '{r}' updated successfully.")
            return redirect('admin_portal:regulation_list')
    else:
        form = RegulationForm(instance=reg)

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': f"Edit Regulation: {reg}",
        'subtitle': 'Modify regulation code, implementation year, or university affiliation.',
        'cancel_url': 'admin_portal:regulation_list',
        'submit_text': 'Save Changes',
    })


@admin_required
def regulation_delete(request, pk):
    reg = get_object_or_404(Regulation, pk=pk)
    if request.method == 'POST':
        name = str(reg)
        reg.delete()
        messages.success(request, f"Regulation '{name}' deleted successfully.")
        return redirect('admin_portal:regulation_list')

    return render(request, 'admin_portal/confirm_delete.html', {
        'object_name': f"Regulation: {reg}",
        'warning_text': "Deleting this regulation will delete all linked semesters, subjects, and study materials.",
        'cancel_url': 'admin_portal:regulation_list',
    })


# ══════════════════════════════════════════════════════════════════
# ACADEMICS: BRANCHES
# ══════════════════════════════════════════════════════════════════

@admin_required
def branch_list(request):
    branches = Branch.objects.annotate(
        student_count=Count('students', distinct=True)
    ).order_by('name')
    return render(request, 'admin_portal/academics/branch_list.html', {'branches': branches})


@admin_required
def branch_create(request):
    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            b = form.save()
            messages.success(request, f"Branch '{b.short_name}' created successfully.")
            return redirect('admin_portal:branch_list')
    else:
        form = BranchForm()

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': 'Add Engineering Branch',
        'subtitle': 'e.g. Computer Science and Engineering (CSE), Mechanical Engineering (MECH).',
        'cancel_url': 'admin_portal:branch_list',
        'submit_text': 'Save Branch',
    })


@admin_required
def branch_edit(request, pk):
    branch = get_object_or_404(Branch, pk=pk)
    if request.method == 'POST':
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            b = form.save()
            messages.success(request, f"Branch '{b.short_name}' updated successfully.")
            return redirect('admin_portal:branch_list')
    else:
        form = BranchForm(instance=branch)

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': f"Edit Branch: {branch.short_name}",
        'subtitle': 'Modify department name or code.',
        'cancel_url': 'admin_portal:branch_list',
        'submit_text': 'Save Changes',
    })


@admin_required
def branch_delete(request, pk):
    branch = get_object_or_404(Branch, pk=pk)
    if request.method == 'POST':
        name = branch.short_name
        branch.delete()
        messages.success(request, f"Branch '{name}' deleted successfully.")
        return redirect('admin_portal:branch_list')

    return render(request, 'admin_portal/confirm_delete.html', {
        'object_name': f"Branch: {branch.name} ({branch.short_name})",
        'warning_text': "Deleting this branch will delete all linked semesters and subjects.",
        'cancel_url': 'admin_portal:branch_list',
    })


# ══════════════════════════════════════════════════════════════════
# ACADEMICS: SEMESTERS
# ══════════════════════════════════════════════════════════════════

@admin_required
def semester_list(request):
    semesters = Semester.objects.select_related('regulation__university', 'branch').annotate(
        subject_count=Count('subjects', distinct=True)
    ).order_by('regulation__university__short_name', 'branch__short_name', 'semester_number')
    return render(request, 'admin_portal/academics/semester_list.html', {'semesters': semesters})


@admin_required
def semester_create(request):
    if request.method == 'POST':
        form = SemesterForm(request.POST)
        if form.is_valid():
            s = form.save()
            messages.success(request, f"Semester '{s}' created successfully.")
            return redirect('admin_portal:semester_list')
    else:
        form = SemesterForm()

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': 'Add Semester to Regulation & Branch',
        'subtitle': 'Map a semester (1-8) to its academic regulation and engineering branch.',
        'cancel_url': 'admin_portal:semester_list',
        'submit_text': 'Save Semester',
    })


@admin_required
def semester_edit(request, pk):
    sem = get_object_or_404(Semester, pk=pk)
    if request.method == 'POST':
        form = SemesterForm(request.POST, instance=sem)
        if form.is_valid():
            s = form.save()
            messages.success(request, f"Semester '{s}' updated successfully.")
            return redirect('admin_portal:semester_list')
    else:
        form = SemesterForm(instance=sem)

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': f"Edit Semester: {sem}",
        'subtitle': 'Modify semester number or parent regulation/branch link.',
        'cancel_url': 'admin_portal:semester_list',
        'submit_text': 'Save Changes',
    })


@admin_required
def semester_delete(request, pk):
    sem = get_object_or_404(Semester, pk=pk)
    if request.method == 'POST':
        name = str(sem)
        sem.delete()
        messages.success(request, f"Semester '{name}' deleted successfully.")
        return redirect('admin_portal:semester_list')

    return render(request, 'admin_portal/confirm_delete.html', {
        'object_name': f"Semester: {sem}",
        'warning_text': "Deleting this semester will delete all linked subjects, units, notes, and question papers.",
        'cancel_url': 'admin_portal:semester_list',
    })


# ══════════════════════════════════════════════════════════════════
# ACADEMICS: SUBJECTS
# ══════════════════════════════════════════════════════════════════

@admin_required
def subject_list(request):
    query = request.GET.get('q', '').strip()
    sem_id = request.GET.get('semester', '')
    subjects = Subject.objects.select_related('semester__regulation__university', 'semester__branch').annotate(
        unit_count=Count('units', distinct=True),
        notes_count=Count('notes', distinct=True),
        pyq_count=Count('question_papers', distinct=True)
    ).order_by('subject_code')

    if query:
        subjects = subjects.filter(
            Q(name__icontains=query) | Q(subject_code__icontains=query)
        )
    if sem_id:
        subjects = subjects.filter(semester_id=sem_id)

    semesters = Semester.objects.select_related('regulation__university', 'branch')

    return render(request, 'admin_portal/academics/subject_list.html', {
        'subjects': subjects,
        'query': query,
        'sem_id': sem_id,
        'semesters': semesters,
    })


@admin_required
def subject_create(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            sub = form.save()
            messages.success(request, f"Subject '{sub.subject_code} - {sub.name}' created successfully.")
            return redirect('admin_portal:subject_list')
    else:
        form = SubjectForm()

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': 'Add New Subject',
        'subtitle': 'e.g. Data Structures (CS301), Operating Systems (CS303).',
        'cancel_url': 'admin_portal:subject_list',
        'submit_text': 'Save Subject',
    })


@admin_required
def subject_edit(request, pk):
    sub = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=sub)
        if form.is_valid():
            s = form.save()
            messages.success(request, f"Subject '{s.subject_code}' updated successfully.")
            return redirect('admin_portal:subject_list')
    else:
        form = SubjectForm(instance=sub)

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': f"Edit Subject: {sub.subject_code} - {sub.name}",
        'subtitle': 'Update credits, code, syllabus description, or parent semester.',
        'cancel_url': 'admin_portal:subject_list',
        'submit_text': 'Save Changes',
    })


@admin_required
def subject_delete(request, pk):
    sub = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        code = sub.subject_code
        sub.delete()
        messages.success(request, f"Subject '{code}' deleted successfully.")
        return redirect('admin_portal:subject_list')

    return render(request, 'admin_portal/confirm_delete.html', {
        'object_name': f"Subject: {sub.subject_code} — {sub.name}",
        'warning_text': "Deleting this subject will delete all linked units, notes, videos, and question papers!",
        'cancel_url': 'admin_portal:subject_list',
    })


# ══════════════════════════════════════════════════════════════════
# ACADEMICS: UNITS & TOPICS
# ══════════════════════════════════════════════════════════════════

@admin_required
def unit_list(request):
    subject_id = request.GET.get('subject', '')
    units = Unit.objects.select_related('subject').annotate(
        topic_count=Count('topics', distinct=True),
        notes_count=Count('notes', distinct=True)
    ).order_by('subject__subject_code', 'unit_number')

    if subject_id:
        units = units.filter(subject_id=subject_id)

    subjects = Subject.objects.all().order_by('subject_code')

    return render(request, 'admin_portal/academics/unit_list.html', {
        'units': units,
        'subjects': subjects,
        'subject_id': subject_id,
    })


@admin_required
def unit_create(request):
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            u = form.save()
            messages.success(request, f"Unit '{u}' created successfully.")
            return redirect('admin_portal:unit_list')
    else:
        form = UnitForm()

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': 'Add Unit to Subject',
        'subtitle': 'Specify unit number (1-5), chapter title, and overview.',
        'cancel_url': 'admin_portal:unit_list',
        'submit_text': 'Save Unit',
    })


@admin_required
def unit_edit(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    if request.method == 'POST':
        form = UnitForm(request.POST, instance=unit)
        if form.is_valid():
            u = form.save()
            messages.success(request, f"Unit '{u}' updated successfully.")
            return redirect('admin_portal:unit_list')
    else:
        form = UnitForm(instance=unit)

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': f"Edit Unit: {unit.name}",
        'subtitle': f"Subject: {unit.subject.subject_code} - {unit.subject.name}",
        'cancel_url': 'admin_portal:unit_list',
        'submit_text': 'Save Changes',
    })


@admin_required
def unit_delete(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    if request.method == 'POST':
        name = str(unit)
        unit.delete()
        messages.success(request, f"Unit '{name}' deleted successfully.")
        return redirect('admin_portal:unit_list')

    return render(request, 'admin_portal/confirm_delete.html', {
        'object_name': f"Unit: {unit.name} ({unit.subject.subject_code})",
        'warning_text': "Deleting this unit will delete all associated topics, notes, and questions.",
        'cancel_url': 'admin_portal:unit_list',
    })


@admin_required
def topic_list(request):
    unit_id = request.GET.get('unit', '')
    topics = Topic.objects.select_related('unit__subject').order_by('unit__subject__subject_code', 'unit__unit_number', 'order')

    if unit_id:
        topics = topics.filter(unit_id=unit_id)

    units = Unit.objects.select_related('subject')

    return render(request, 'admin_portal/academics/topic_list.html', {
        'topics': topics,
        'units': units,
        'unit_id': unit_id,
    })


@admin_required
def topic_create(request):
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            t = form.save()
            messages.success(request, f"Topic '{t.name}' created successfully.")
            return redirect('admin_portal:topic_list')
    else:
        form = TopicForm()

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': 'Add Specific Topic',
        'subtitle': 'Map a technical concept/subtopic to a unit.',
        'cancel_url': 'admin_portal:topic_list',
        'submit_text': 'Save Topic',
    })


@admin_required
def topic_edit(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    if request.method == 'POST':
        form = TopicForm(request.POST, instance=topic)
        if form.is_valid():
            t = form.save()
            messages.success(request, f"Topic '{t.name}' updated successfully.")
            return redirect('admin_portal:topic_list')
    else:
        form = TopicForm(instance=topic)

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': f"Edit Topic: {topic.name}",
        'subtitle': f"Unit: {topic.unit.name}",
        'cancel_url': 'admin_portal:topic_list',
        'submit_text': 'Save Changes',
    })


@admin_required
def topic_delete(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    if request.method == 'POST':
        name = topic.name
        topic.delete()
        messages.success(request, f"Topic '{name}' deleted successfully.")
        return redirect('admin_portal:topic_list')

    return render(request, 'admin_portal/confirm_delete.html', {
        'object_name': f"Topic: {topic.name}",
        'warning_text': "Deleting this topic will remove its mapping from linked notes and videos.",
        'cancel_url': 'admin_portal:topic_list',
    })


# ══════════════════════════════════════════════════════════════════
# RESOURCES: STUDY NOTES
# ══════════════════════════════════════════════════════════════════

@admin_required
def note_list(request):
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')
    subject_id = request.GET.get('subject', '')

    notes = Note.objects.select_related('subject', 'unit', 'uploaded_by').order_by('-created_at')

    if query:
        notes = notes.filter(Q(title__icontains=query) | Q(subject__name__icontains=query) | Q(subject__subject_code__icontains=query))
    if status_filter == 'approved':
        notes = notes.filter(is_approved=True)
    elif status_filter == 'pending':
        notes = notes.filter(is_approved=False)
    if subject_id:
        notes = notes.filter(subject_id=subject_id)

    paginator = Paginator(notes, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    subjects = Subject.objects.all()

    return render(request, 'admin_portal/resources/note_list.html', {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
        'subject_id': subject_id,
        'subjects': subjects,
    })


@admin_required
def note_create(request):
    if request.method == 'POST':
        form = NoteForm(request.POST, request.FILES)
        if form.is_valid():
            n = form.save(commit=False)
            n.uploaded_by = request.user
            n.save()
            messages.success(request, f"Note '{n.title}' uploaded successfully.")
            return redirect('admin_portal:note_list')
    else:
        form = NoteForm(initial={'is_approved': True})

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': 'Upload New Study Note / PDF',
        'subtitle': 'Upload chapter notes, formula sheets, or hand-written unit summaries.',
        'cancel_url': 'admin_portal:note_list',
        'submit_text': 'Upload Note',
    })


@admin_required
def note_edit(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'POST':
        form = NoteForm(request.POST, request.FILES, instance=note)
        if form.is_valid():
            n = form.save()
            messages.success(request, f"Note '{n.title}' updated successfully.")
            return redirect('admin_portal:note_list')
    else:
        form = NoteForm(instance=note)

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': f"Edit Note: {note.title}",
        'subtitle': f"Subject: {note.subject.subject_code} - {note.subject.name}",
        'cancel_url': 'admin_portal:note_list',
        'submit_text': 'Save Changes',
    })


@admin_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'POST':
        title = note.title
        note.delete()
        messages.success(request, f"Note '{title}' deleted successfully.")
        return redirect('admin_portal:note_list')

    return render(request, 'admin_portal/confirm_delete.html', {
        'object_name': f"Study Note: {note.title}",
        'warning_text': "This file and its download count records will be deleted.",
        'cancel_url': 'admin_portal:note_list',
    })


@admin_required
def note_toggle_approve(request, pk):
    note = get_object_or_404(Note, pk=pk)
    note.is_approved = not note.is_approved
    note.save()
    status_str = "approved" if note.is_approved else "moved to pending"
    messages.success(request, f"Note '{note.title}' has been {status_str}.")
    return redirect('admin_portal:note_list')


# ══════════════════════════════════════════════════════════════════
# RESOURCES: VIDEO LECTURES
# ═══════════════════════════════════════════════════

@admin_required
def video_list(request):
    videos = Video.objects.select_related('subject', 'unit').order_by('-created_at')
    return render(request, 'admin_portal/resources/video_list.html', {'videos': videos})


@admin_required
def video_create(request):
    if request.method == 'POST':
        form = VideoForm(request.POST)
        if form.is_valid():
            v = form.save()
            messages.success(request, f"Video '{v.title}' added successfully.")
            return redirect('admin_portal:video_list')
    else:
        form = VideoForm(initial={'is_verified': True})

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': 'Add Curated YouTube Video Lecture',
        'subtitle': 'Link an accredited video explanation or derivation to a subject.',
        'cancel_url': 'admin_portal:video_list',
        'submit_text': 'Add Video',
    })


@admin_required
def video_edit(request, pk):
    video = get_object_or_404(Video, pk=pk)
    if request.method == 'POST':
        form = VideoForm(request.POST, instance=video)
        if form.is_valid():
            v = form.save()
            messages.success(request, f"Video '{v.title}' updated successfully.")
            return redirect('admin_portal:video_list')
    else:
        form = VideoForm(instance=video)

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': f"Edit Video: {video.title}",
        'subtitle': f"YouTube ID: {video.youtube_id}",
        'cancel_url': 'admin_portal:video_list',
        'submit_text': 'Save Changes',
    })


@admin_required
def video_delete(request, pk):
    video = get_object_or_404(Video, pk=pk)
    if request.method == 'POST':
        title = video.title
        video.delete()
        messages.success(request, f"Video '{title}' deleted successfully.")
        return redirect('admin_portal:video_list')

    return render(request, 'admin_portal/confirm_delete.html', {
        'object_name': f"Video Lecture: {video.title}",
        'warning_text': "This will remove the video reference from student study material views.",
        'cancel_url': 'admin_portal:video_list',
    })


# ══════════════════════════════════════════════════════════════════
# PYQS: QUESTION PAPERS
# ══════════════════════════════════════════════════════════════════

@admin_required
def paper_list(request):
    papers = QuestionPaper.objects.select_related('subject').annotate(
        q_count=Count('questions', distinct=True)
    ).order_by('-year', 'subject__subject_code')
    return render(request, 'admin_portal/pyqs/paper_list.html', {'papers': papers})


@admin_required
def paper_create(request):
    if request.method == 'POST':
        form = QuestionPaperForm(request.POST, request.FILES)
        if form.is_valid():
            p = form.save()
            messages.success(request, f"Question Paper '{p}' uploaded successfully.")
            return redirect('admin_portal:paper_list')
    else:
        form = QuestionPaperForm(initial={'is_verified': True})

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': 'Upload University Question Paper PDF',
        'subtitle': 'Select subject, year (e.g. 2024), exam type (End Semester, Mid 1), and upload PDF.',
        'cancel_url': 'admin_portal:paper_list',
        'submit_text': 'Upload Paper',
    })


@admin_required
def paper_edit(request, pk):
    paper = get_object_or_404(QuestionPaper, pk=pk)
    if request.method == 'POST':
        form = QuestionPaperForm(request.POST, request.FILES, instance=paper)
        if form.is_valid():
            p = form.save()
            messages.success(request, f"Question Paper '{p}' updated successfully.")
            return redirect('admin_portal:paper_list')
    else:
        form = QuestionPaperForm(instance=paper)

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': f"Edit Question Paper: {paper}",
        'subtitle': 'Modify paper year, exam type, or replace the attached PDF file.',
        'cancel_url': 'admin_portal:paper_list',
        'submit_text': 'Save Changes',
    })


@admin_required
def paper_delete(request, pk):
    paper = get_object_or_404(QuestionPaper, pk=pk)
    if request.method == 'POST':
        name = str(paper)
        paper.delete()
        messages.success(request, f"Question Paper '{name}' deleted successfully.")
        return redirect('admin_portal:paper_list')

    return render(request, 'admin_portal/confirm_delete.html', {
        'object_name': f"Question Paper: {paper}",
        'warning_text': "Deleting this question paper will also delete all individual questions extracted from it.",
        'cancel_url': 'admin_portal:paper_list',
    })


# ══════════════════════════════════════════════════════════════════
# PYQS: INDIVIDUAL QUESTIONS
# ══════════════════════════════════════════════════════════════════

@admin_required
def question_list(request):
    paper_id = request.GET.get('paper', '')
    questions = PYQQuestion.objects.select_related('paper__subject', 'unit').order_by('-importance_score')

    if paper_id:
        questions = questions.filter(paper_id=paper_id)

    paginator = Paginator(questions, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    papers = QuestionPaper.objects.select_related('subject')

    return render(request, 'admin_portal/pyqs/question_list.html', {
        'page_obj': page_obj,
        'papers': papers,
        'paper_id': paper_id,
    })


@admin_required
def question_create(request):
    initial = {}
    if request.GET.get('paper'):
        initial['paper'] = request.GET.get('paper')

    if request.method == 'POST':
        form = PYQQuestionForm(request.POST)
        if form.is_valid():
            q = form.save()
            messages.success(request, "PYQ Question added successfully.")
            return redirect('admin_portal:question_list')
    else:
        form = PYQQuestionForm(initial=initial)

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': 'Add Individual PYQ Question',
        'subtitle': 'Specify question text, marks (10/5/2), frequency, and model solution derivation.',
        'cancel_url': 'admin_portal:question_list',
        'submit_text': 'Save Question',
    })


@admin_required
def question_edit(request, pk):
    question = get_object_or_404(PYQQuestion, pk=pk)
    if request.method == 'POST':
        form = PYQQuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, "PYQ Question updated successfully.")
            return redirect('admin_portal:question_list')
    else:
        form = PYQQuestionForm(instance=question)

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': 'Edit PYQ Question',
        'subtitle': f"From Paper: {question.paper}",
        'cancel_url': 'admin_portal:question_list',
        'submit_text': 'Save Changes',
    })


@admin_required
def question_delete(request, pk):
    question = get_object_or_404(PYQQuestion, pk=pk)
    if request.method == 'POST':
        question.delete()
        messages.success(request, "PYQ Question deleted successfully.")
        return redirect('admin_portal:question_list')

    return render(request, 'admin_portal/confirm_delete.html', {
        'object_name': f"PYQ Question: {question.question_text[:80]}...",
        'warning_text': "This question will be removed from the important questions database.",
        'cancel_url': 'admin_portal:question_list',
    })


# ══════════════════════════════════════════════════════════════════
# QUIZZES & QUIZ QUESTIONS
# ══════════════════════════════════════════════════════════════════

@admin_required
def quiz_list(request):
    quizzes = Quiz.objects.select_related('subject', 'unit').annotate(
        q_count=Count('questions', distinct=True),
        attempt_count=Count('attempts', distinct=True)
    ).order_by('-created_at')
    return render(request, 'admin_portal/quizzes/quiz_list.html', {'quizzes': quizzes})


@admin_required
def quiz_create(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save()
            messages.success(request, f"Quiz '{quiz.title}' created successfully! Now add questions.")
            return redirect('admin_portal:quiz_question_list', quiz_id=quiz.id)
    else:
        form = QuizForm(initial={'is_active': True})

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': 'Create New Practice Quiz',
        'subtitle': 'Set quiz title, subject, duration, pass marks, and difficulty level.',
        'cancel_url': 'admin_portal:quiz_list',
        'submit_text': 'Create Quiz',
    })


@admin_required
def quiz_edit(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            q = form.save()
            messages.success(request, f"Quiz '{q.title}' updated successfully.")
            return redirect('admin_portal:quiz_list')
    else:
        form = QuizForm(instance=quiz)

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': f"Edit Quiz: {quiz.title}",
        'subtitle': f"Subject: {quiz.subject.subject_code} - {quiz.subject.name}",
        'cancel_url': 'admin_portal:quiz_list',
        'submit_text': 'Save Changes',
    })


@admin_required
def quiz_delete(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    if request.method == 'POST':
        title = quiz.title
        quiz.delete()
        messages.success(request, f"Quiz '{title}' deleted successfully.")
        return redirect('admin_portal:quiz_list')

    return render(request, 'admin_portal/confirm_delete.html', {
        'object_name': f"Quiz: {quiz.title}",
        'warning_text': "Deleting this quiz will delete all its questions and student attempt records.",
        'cancel_url': 'admin_portal:quiz_list',
    })


@admin_required
def quiz_question_list(request, quiz_id):
    quiz = get_object_or_404(Quiz.objects.select_related('subject'), pk=quiz_id)
    questions = quiz.questions.all().order_by('order')
    return render(request, 'admin_portal/quizzes/question_list.html', {
        'quiz': quiz,
        'questions': questions,
    })


@admin_required
def quiz_question_create(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    if request.method == 'POST':
        form = QuizQuestionForm(request.POST)
        if form.is_valid():
            q = form.save(commit=False)
            q.quiz = quiz
            q.save()
            messages.success(request, "Quiz Question added successfully.")
            return redirect('admin_portal:quiz_question_list', quiz_id=quiz.id)
    else:
        next_order = quiz.questions.count() + 1
        form = QuizQuestionForm(initial={'quiz': quiz, 'order': next_order})

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': f"Add Question to: {quiz.title}",
        'subtitle': 'Define question text, options A-D, correct option, and explanation.',
        'cancel_link': reverse('admin_portal:quiz_question_list', kwargs={'quiz_id': quiz.id}),
        'submit_text': 'Add Question',
    })


@admin_required
def quiz_question_edit(request, pk):
    question = get_object_or_404(QuizQuestion.objects.select_related('quiz'), pk=pk)
    if request.method == 'POST':
        form = QuizQuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, "Quiz Question updated successfully.")
            return redirect('admin_portal:quiz_question_list', quiz_id=question.quiz.id)
    else:
        form = QuizQuestionForm(instance=question)

    return render(request, 'admin_portal/generic_form.html', {
        'form': form,
        'title': f"Edit Question: Q{question.order}",
        'subtitle': f"Quiz: {question.quiz.title}",
        'cancel_link': reverse('admin_portal:quiz_question_list', kwargs={'quiz_id': question.quiz.id}),
        'submit_text': 'Save Changes',
    })


@admin_required
def quiz_question_delete(request, pk):
    question = get_object_or_404(QuizQuestion.objects.select_related('quiz'), pk=pk)
    quiz_id = question.quiz.id
    if request.method == 'POST':
        question.delete()
        messages.success(request, "Quiz Question deleted successfully.")
        return redirect('admin_portal:quiz_question_list', quiz_id=quiz_id)

    return render(request, 'admin_portal/confirm_delete.html', {
        'object_name': f"Quiz Question: {question.question_text[:80]}...",
        'warning_text': "This question will be removed from the quiz.",
        'cancel_link': reverse('admin_portal:quiz_question_list', kwargs={'quiz_id': quiz_id}),
    })


# ══════════════════════════════════════════════════════════════════
# PLATFORM ANALYTICS & CENTRALIZED OVERVIEW
# ══════════════════════════════════════════════════════════════════

@admin_required
def analytics(request):
    """Centralized analytics and platform metrics."""
    branch_stats = Branch.objects.annotate(
        student_count=Count('students', distinct=True)
    ).order_by('-student_count')

    univ_stats = University.objects.annotate(
        student_count=Count('students', distinct=True)
    ).order_by('-student_count')

    subject_notes_stats = Subject.objects.annotate(
        notes_count=Count('notes', distinct=True),
        paper_count=Count('question_papers', distinct=True)
    ).order_by('-notes_count')[:10]

    recent_attempts = QuizAttempt.objects.select_related('student', 'quiz').order_by('-id')[:10]
    recent_scans = ScannedQuestion.objects.select_related('student').order_by('-created_at')[:8]

    return render(request, 'admin_portal/analytics.html', {
        'branch_stats': branch_stats,
        'univ_stats': univ_stats,
        'subject_notes_stats': subject_notes_stats,
        'recent_attempts': recent_attempts,
        'recent_scans': recent_scans,
    })
