"""
Forms for ErVeda Admin Portal.
Provides form controls for all centralized administration CRUD operations.
"""
from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm
from academics.models import University, Regulation, Branch, Semester, Subject, Unit, Topic
from resources.models import Note, Video
from pyqs.models import QuestionPaper, PYQQuestion
from quizzes.models import Quiz, QuizQuestion

Student = get_user_model()


class AdminLoginForm(forms.Form):
    """Admin-specific login form requiring staff credentials."""
    username = forms.CharField(
        label="Admin Username or Email",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter admin username or email',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter password',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Invalid credentials. Please verify your username and password.")
            if not user.is_staff and not user.is_superuser:
                raise forms.ValidationError("Access denied. Only authorized staff and administrators can access the Admin Portal.")
            if not user.is_active:
                raise forms.ValidationError("This administrative account has been deactivated.")
            cleaned_data['user'] = user

        return cleaned_data


class AdminStudentForm(forms.ModelForm):
    """Admin form for adding/editing student accounts."""
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Leave blank to keep current password (or set new password)',
        }),
        help_text="Leave blank if editing without changing password."
    )

    class Meta:
        model = Student
        fields = [
            'username', 'email', 'first_name', 'last_name', 'gender',
            'phone_number', 'college_name', 'university', 'regulation',
            'branch', 'current_year', 'current_semester', 'is_active', 'is_staff'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'college_name': forms.TextInput(attrs={'class': 'form-control'}),
            'university': forms.Select(attrs={'class': 'form-select'}),
            'regulation': forms.Select(attrs={'class': 'form-select'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'current_year': forms.Select(attrs={'class': 'form-select'}),
            'current_semester': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        student = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            student.set_password(password)
        if commit:
            student.save()
        return student


class UniversityForm(forms.ModelForm):
    class Meta:
        model = University
        fields = ['name', 'short_name', 'state', 'website', 'logo', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Jawaharlal Nehru Technological University Hyderabad'}),
            'short_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. JNTUH'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Telangana'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://jntuh.ac.in'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RegulationForm(forms.ModelForm):
    class Meta:
        model = Regulation
        fields = ['university', 'name', 'year', 'description', 'is_active']
        widgets = {
            'university': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. R22'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2022'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional details about this regulation'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name', 'short_name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Computer Science and Engineering'}),
            'short_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CSE'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SemesterForm(forms.ModelForm):
    class Meta:
        model = Semester
        fields = ['regulation', 'branch', 'semester_number', 'year_of_study']
        widgets = {
            'regulation': forms.Select(attrs={'class': 'form-select'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'semester_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 8, 'placeholder': '1 to 8'}),
            'year_of_study': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 4, 'placeholder': '1 to 4'}),
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['semester', 'name', 'subject_code', 'credits', 'subject_type', 'description', 'is_active']
        widgets = {
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Data Structures'}),
            'subject_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CS301'}),
            'credits': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 3'}),
            'subject_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['subject', 'unit_number', 'name', 'description']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'unit_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5, 'placeholder': '1 to 5'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Trees and Graphs'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['unit', 'name', 'description', 'order']
        widgets = {
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Binary Search Trees & AVL Balancing'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
        }


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'note_type', 'description', 'subject', 'unit', 'topic', 'pdf_file', 'thumbnail', 'is_approved']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Unit 3 Complete Notes on Graphs'}),
            'note_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'topic': forms.Select(attrs={'class': 'form-select'}),
            'pdf_file': forms.FileInput(attrs={'class': 'form-control'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
            'is_approved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'youtube_url', 'subject', 'unit', 'topic', 'channel_name', 'difficulty', 'video_type', 'is_verified']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Dijkstra Shortest Path Algorithm Explained'}),
            'youtube_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.youtube.com/watch?v=...'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'topic': forms.Select(attrs={'class': 'form-select'}),
            'channel_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MIT OpenCourseWare'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'video_type': forms.Select(attrs={'class': 'form-select'}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class QuestionPaperForm(forms.ModelForm):
    class Meta:
        model = QuestionPaper
        fields = ['subject', 'year', 'exam_type', 'pdf_file', 'is_verified']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2024'}),
            'exam_type': forms.Select(attrs={'class': 'form-select'}),
            'pdf_file': forms.FileInput(attrs={'class': 'form-control'}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PYQQuestionForm(forms.ModelForm):
    class Meta:
        model = PYQQuestion
        fields = ['paper', 'unit', 'topic', 'question_text', 'question_type', 'marks', 'frequency_count', 'solution_text']
        widgets = {
            'paper': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'topic': forms.Select(attrs={'class': 'form-select'}),
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter full question statement...'}),
            'question_type': forms.Select(attrs={'class': 'form-select'}),
            'marks': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 10'}),
            'frequency_count': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1'}),
            'solution_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Step-by-step verified solution derivation...'}),
        }

    def save(self, commit=True):
        question = super().save(commit=False)
        question.calculate_importance()
        if commit:
            question.save()
        return question


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'quiz_type', 'difficulty', 'subject', 'unit', 'topic', 'time_limit_minutes', 'total_marks', 'pass_marks', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Unit 2 Midterm Practice Quiz'}),
            'quiz_type': forms.Select(attrs={'class': 'form-select'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'topic': forms.Select(attrs={'class': 'form-select'}),
            'time_limit_minutes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '30'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '20'}),
            'pass_marks': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '10'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class QuizQuestionForm(forms.ModelForm):
    option_a = forms.CharField(label="Option A", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option A'}))
    option_b = forms.CharField(label="Option B", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option B'}))
    option_c = forms.CharField(label="Option C", required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option C'}))
    option_d = forms.CharField(label="Option D", required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option D'}))

    class Meta:
        model = QuizQuestion
        fields = ['quiz', 'question_text', 'question_type', 'correct_answer', 'explanation', 'marks', 'order']
        widgets = {
            'quiz': forms.Select(attrs={'class': 'form-select'}),
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Question text...'}),
            'question_type': forms.Select(attrs={'class': 'form-select'}),
            'correct_answer': forms.Select(choices=[('A', 'Option A'), ('B', 'Option B'), ('C', 'Option C'), ('D', 'Option D')], attrs={'class': 'form-select'}),
            'explanation': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Explanation for correct answer...'}),
            'marks': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.options:
            opts = self.instance.options
            self.fields['option_a'].initial = opts.get('A', '')
            self.fields['option_b'].initial = opts.get('B', '')
            self.fields['option_c'].initial = opts.get('C', '')
            self.fields['option_d'].initial = opts.get('D', '')

    def save(self, commit=True):
        question = super().save(commit=False)
        question.options = {
            'A': self.cleaned_data.get('option_a', '').strip(),
            'B': self.cleaned_data.get('option_b', '').strip(),
            'C': self.cleaned_data.get('option_c', '').strip(),
            'D': self.cleaned_data.get('option_d', '').strip(),
        }
        if commit:
            question.save()
        return question
