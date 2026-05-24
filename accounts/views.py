# accounts/views.py
from django.contrib.auth.decorators import login_required
from core.models import Application, StudentGuardian
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.utils import timezone
from .forms import ParentRegistrationForm

# Create your views here.

from core.models import Application

def register(request):
    if request.method == 'POST':
        form = ParentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Link any applications with matching email
            email = form.cleaned_data.get('email')
            Application.objects.filter(parent_email=email, user__isnull=True).update(user=user)
            login(request, user)
            messages.success(request, 'Account created successfully. Welcome!')
            return redirect('accounts:dashboard')
    else:
        form = ParentRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def dashboard(request):

    applications = Application.objects.filter(user=request.user).order_by('-submitted_at')
    guardian_links = StudentGuardian.objects.filter(
        guardian=request.user
    ).select_related('student__class_group').order_by('student__last_name')

    return render(request, 'accounts/dashboard.html', {
        'applications': applications,
        'guardian_links': guardian_links,
    })
from core.models import Student
import uuid

def generate_admission_number():
    return f"IVT{timezone.now().year}{uuid.uuid4().hex[:6].upper()}"

@login_required
def accept_offer(request, app_id):
    application = get_object_or_404(Application, id=app_id, user=request.user, status='offered')
    application.status = 'accepted'
    application.offer_response = 'accept'
    application.offer_response_date = timezone.now()
    application.save()

    # Create student record if not already existing
    if not Student.objects.filter(first_name=application.student_first_name,
                                  last_name=application.student_last_name,
                                  date_of_birth=application.student_date_of_birth).exists():
        Student.objects.create(
            first_name=application.student_first_name,
            last_name=application.student_last_name,
            date_of_birth=application.student_date_of_birth,
            admission_number=generate_admission_number(),
            class_group=None,  # assign later
            is_active=True,
        )
    messages.success(request, 'Congratulations! You have accepted the offer.')
    return redirect('accounts:application_detail', app_id=app_id)

@login_required
def decline_offer(request, app_id):
    application = get_object_or_404(Application, id=app_id, user=request.user, status='offered')
    application.status = 'declined'
    application.offer_response = 'decline'
    application.offer_response_date = timezone.now()
    application.save()
    messages.info(request, 'You have declined the offer.')
    return redirect('accounts:application_detail', app_id=app_id)
from django.shortcuts import get_object_or_404
from core.forms import ApplicationDocumentForm  # We'll create this form

@login_required
def application_detail(request, app_id):
    application = get_object_or_404(Application, id=app_id, user=request.user)
    # Handle document upload
    if request.method == 'POST' and 'upload_docs' in request.POST:
        form = ApplicationDocumentForm(request.POST, request.FILES, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, 'Documents updated.')
            return redirect('accounts:application_detail', app_id=app_id)
    else:
        form = ApplicationDocumentForm(instance=application)

    return render(request, 'accounts/application_detail.html', {
        'application': application,
        'form': form,
    })
# accounts/views.py (add the function)
from .forms import StaffRegistrationForm

def register_staff(request):
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, 
                'Registration submitted. An administrator will review and activate your account.'
            )
            return redirect('core:home')
    else:
        form = StaffRegistrationForm()
    return render(request, 'accounts/register_staff.html', {'form': form})

from django.contrib.auth import logout

@login_required
def user_profile(request):
    """
    Allows any authenticated user to view their account details.
    """
    context = {
        'user': request.user,
        # Get linked data based on role
        'teacher_profile': getattr(request.user, 'teacher_profile', None),
        'student_profile': getattr(request.user, 'student_profile', None),
        'wards': request.user.wards.select_related('student__class_group').all() if request.user.role == 'parent' else [],
    }
    return render(request, 'accounts/user_profile.html', context)


@login_required
def delete_account(request):
    """
    Allows a user to permanently delete their own account.
    Requires POST for safety (no accidental GET deletion).
    """
    if request.method == 'POST':
        user = request.user
        # Log them out first
        logout(request)
        # Delete the user (cascades to related objects based on on_delete settings)
        user.delete()
        messages.success(request, 'Your account has been permanently deleted.')
        return redirect('core:home')
    return render(request, 'accounts/delete_account_confirm.html')