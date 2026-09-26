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
    """Step 2: Academic info form after registration."""

    class Meta:
        model = Student
        fields = ['university', 'regulation', 'branch', 'current_year',
                  'current_semester', 'college_name', 'phone_number', 'gender']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'university',
            Row(
                Column('regulation', css_class='col-md-6'),
                Column('branch', css_class='col-md-6'),
            ),
            Row(
                Column('current_year', css_class='col-md-6'),
                Column('current_semester', css_class='col-md-6'),
            ),
            Row(
                Column('college_name', css_class='col-md-6'),
                Column('gender', css_class='col-md-6'),
            ),
            'phone_number',
            Submit('submit', 'Save Academic Info', css_class='btn btn-success btn-lg w-100 mt-3')
        )

        # Add empty label
        self.fields['university'].empty_label = '-- Select University --'
        self.fields['regulation'].empty_label = '-- Select Regulation --'
        self.fields['branch'].empty_label = '-- Select Branch --'
        self.fields['current_year'].empty_label = '-- Select Year --'
        self.fields['current_semester'].empty_label = '-- Select Semester --'
        self.fields['gender'].empty_label = '-- Select Gender (for avatar) --'


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
