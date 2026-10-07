"""
Forms for Student registration and profile.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field, Div, HTML

from .models import Student
from academics.models import University, Regulation, Branch


class StudentRegistrationForm(UserCreationForm):
    """Step 1: Basic info registration form."""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'your@email.com'})
    )
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Your first name'})
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Your last name'})
    )

    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
            ),
            'username',
            'email',
            'password1',
            'password2',
            Submit('submit', 'Create Account', css_class='btn btn-primary btn-lg w-100 mt-3')
        )
        # Clean up help texts
        self.fields['username'].help_text = 'Letters, digits and @/./+/-/_ only.'
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Student.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email


class AcademicProfileForm(forms.ModelForm):
    """Step 2: Academic info form for student setup and profile editing."""

    class Meta:
        model = Student
        fields = ['university', 'regulation', 'branch', 'current_year',
                  'current_semester', 'gender', 'college_name']
        widgets = {
            'university': forms.Select(attrs={'class': 'form-select form-select-lg shadow-none'}),
            'regulation': forms.Select(attrs={'class': 'form-select form-select-lg shadow-none'}),
            'branch': forms.Select(attrs={'class': 'form-select form-select-lg shadow-none'}),
            'current_year': forms.Select(attrs={'class': 'form-select form-select-lg shadow-none'}),
            'current_semester': forms.Select(attrs={'class': 'form-select form-select-lg shadow-none'}),
            'gender': forms.Select(attrs={'class': 'form-select form-select-lg shadow-none'}),
            'college_name': forms.TextInput(attrs={'class': 'form-control shadow-none', 'placeholder': 'e.g. JNTUH College of Engineering'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add friendly empty labels
        self.fields['university'].empty_label = '-- Select University --'
        self.fields['regulation'].empty_label = '-- Select Regulation --'
        self.fields['branch'].empty_label = '-- Select Engineering Branch --'
        self.fields['current_year'].empty_label = '-- Select Year of Study --'
        self.fields['current_semester'].empty_label = '-- Select Semester --'
        self.fields['gender'].empty_label = '-- Select Gender (for avatar) --'

        # Auto-select JNTUH if it's the only university
        jntuh = University.objects.first()
        if jntuh and not self.initial.get('university'):
            self.initial['university'] = jntuh.id

        # Auto-select R25 as recommended regulation if none selected
        r25 = Regulation.objects.filter(name='R25').first()
        if r25 and not self.initial.get('regulation'):
            self.initial['regulation'] = r25.id


class StudentLoginForm(AuthenticationForm):
    """Custom login form supporting username or email."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'password',
            Submit('submit', 'Sign In', css_class='btn btn-primary btn-lg w-100 mt-3')
        )
        self.fields['username'].label = 'Username or Email'
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Enter username or email',
            'autofocus': True,
        })
        self.fields['password'].widget.attrs.update({
            'placeholder': 'Enter your password',
        })

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            return username.strip()
        return username


class ProfilePhotoForm(forms.ModelForm):
    """Update profile photo."""

    class Meta:
        model = Student
        fields = ['profile_photo']
