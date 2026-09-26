"""
Views for student authentication and profile management.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy

from .models import Student
from .forms import StudentRegistrationForm, AcademicProfileForm, StudentLoginForm


def landing(request):
    """Public landing page."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return render(request, 'landing.html')


def register(request):
    """Student registration — Step 1: Basic info."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='accounts.backends.EmailOrUsernameModelBackend')
            messages.success(request, f'Welcome {user.display_name}! Please complete your academic profile.')
            return redirect('accounts:setup_profile')
    else:
        form = StudentRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def setup_profile(request):
    """Step 2: Academic profile setup after registration."""
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    student = request.user

    if request.method == 'POST':
        form = AcademicProfileForm(request.POST, instance=student)
        if form.is_valid():
            student = form.save(commit=False)
            student.profile_completed = True
            student.save()
            messages.success(request, 'Academic profile saved! Welcome to ErVeda 🎓')
            return redirect('dashboard:home')
    else:
        form = AcademicProfileForm(instance=student)

    return render(request, 'accounts/setup_profile.html', {'form': form})


def student_login(request):
    """Student login view."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = StudentLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'dashboard:home')
            messages.success(request, f'Welcome back, {user.display_name}!')
            return redirect(next_url)
    else:
        form = StudentLoginForm(request)

    return render(request, 'accounts/login.html', {'form': form})


def student_logout(request):
    """Logout and redirect to landing."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile(request):
    """View and edit student profile."""
    student = request.user

    if request.method == 'POST':
        form = AcademicProfileForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = AcademicProfileForm(instance=student)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'student': student,
    })
