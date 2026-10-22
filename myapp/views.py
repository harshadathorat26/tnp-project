from urllib import request

from django.shortcuts import render ,redirect, HttpResponse
from django.contrib.auth import authenticate, login ,logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from .models import StudentProfile
from .models import Resume
from .forms import ResumeForm
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Notification
from .models import PlacementDrive, JobApplication

# for admin dashboard
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
# Create your views here.

def index(request):
    context = {
    }#context ia a python dictonary which is used to send data from views.py to html file by using key name in html file. 
    #render is used to display a html page.
    return render(request, "index.html", context)
    # return HttpResponse("this is homepage")

@login_required
def profile(request):
  
    return render(request, "profile.html")


@login_required
def notification(request):
    notifications = Notification.objects.all().order_by('-date')

    return render(request, 'notification.html', {
        'notifications': notifications
    })


@login_required
def application(request):
    drives = PlacementDrive.objects.filter(
        deadline__gte=timezone.localdate()
    ).order_by('deadline')

    my_applications = JobApplication.objects.filter(
        student=request.user
    ).select_related('drive').order_by('-applied_at')

    applied_drive_ids = my_applications.values_list(
        'drive_id', flat=True
    )

    return render(request, 'application.html', {
        'drives': drives,
        'my_applications': my_applications,
        'applied_drive_ids': applied_drive_ids,
    })

@login_required
def apply_for_drive(request, drive_id):

    if request.method != 'POST':
        return redirect('application')

    drive = get_object_or_404(PlacementDrive, id=drive_id)

    if drive.deadline < timezone.localdate():
        messages.error(request, 'The application deadline has passed.')
        return redirect('application')

    application_obj, created = JobApplication.objects.get_or_create(
        student=request.user,
        drive=drive
    )

    if created:
        messages.success(
            request,
            f'You successfully applied for {drive.company_name}!'
        )
    else:
        messages.warning(
            request,
            'You have already applied for this placement drive.'
        )

    return redirect('application')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        messages.error(request, 'Invalid username or password.')
    return render(request, "login.html")


@login_required
def dashboard(request):
    total_drives = PlacementDrive.objects.filter(
        deadline__gte=timezone.localdate()
    ).count()

    total_applications = JobApplication.objects.filter(
        student=request.user
    ).count()

    shortlisted = JobApplication.objects.filter(
        student=request.user,
        status='Shortlisted'
    ).count()

    total_notifications = Notification.objects.count()

    recent_drives = PlacementDrive.objects.filter(
        deadline__gte=timezone.localdate()
    ).order_by('deadline')[:3]

    recent_notifications = Notification.objects.order_by('-date')[:3]

    return render(request, 'dashboard.html', {
        'total_drives': total_drives,
        'total_applications': total_applications,
        'shortlisted': shortlisted,
        'total_notifications': total_notifications,
        'recent_drives': recent_drives,
        'recent_notifications': recent_notifications,
    })

def logout_view(request):
    auth_logout(request)
    return render(request,'logout.html')


@login_required
def profile(request):
    student, created = StudentProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': request.user.get_full_name(),
            'phone': '',
            'course': 'MCA',
            'skills': ''
        }
    )

    if request.method == 'POST':
        student.full_name = request.POST.get('full_name')
        student.phone = request.POST.get('phone')
        student.course = request.POST.get('course')
        student.skills = request.POST.get('skills')
        student.save()

        return redirect('profile')

    return render(request, 'profile.html', {'student': student})

@login_required
def resume(request):
    try:
        resume = Resume.objects.get(user=request.user)
    except Resume.DoesNotExist:
        resume = None

    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES, instance=resume)

        if form.is_valid():
            resume_obj = form.save(commit=False)
            resume_obj.user = request.user
            resume_obj.save()

            return redirect('resume')

    else:
        form = ResumeForm(instance=resume)

    return render(request, 'resume.html', {
        'form': form,
        'resume': resume
    })

@login_required
def delete_resume(request):
    try:
        resume = Resume.objects.get(user=request.user)
    except Resume.DoesNotExist:
        resume = None

    if resume:
        resume.resume_file.delete()
        resume.delete()

    return redirect('resume')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not all([first_name, username, email, password, confirm_password]):
            messages.error(request, 'Please fill in all fields.')

        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')

        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered.')

        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')

        elif len(password) < 8:
            messages.error(request, 'Password must contain at least 8 characters.')

        else:
            User.objects.create_user(
                username=username,
                first_name=first_name,
                email=email,
                password=password
            )

            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login_view')

    return render(request, 'register.html')

@staff_member_required
def admin_dashboard(request):

    # Overall statistics
    total_students = StudentProfile.objects.count()

    total_companies = (
        PlacementDrive.objects
        .values('company_name')
        .distinct()
        .count()
    )

    total_drives = PlacementDrive.objects.count()

    active_drives = PlacementDrive.objects.filter(
        deadline__gte=timezone.localdate()
    ).count()

    total_applications = JobApplication.objects.count()

    selected = JobApplication.objects.filter(
        status='Selected'
    ).count()

    # Application status analysis
    application_status = (
        JobApplication.objects
        .values('status')
        .annotate(count=Count('id'))
        .order_by('status')
    )

    # Companies receiving the most applications
    top_companies = (
        PlacementDrive.objects
        .values('company_name')
        .annotate(application_count=Count('jobapplication'))
        .order_by('-application_count')[:5]
    )

    # Recent applications
    recent_applications = (
        JobApplication.objects
        .select_related('student', 'drive')
        .order_by('-applied_at')[:5]
    )

    context = {
        'total_students': total_students,
        'total_companies': total_companies,
        'total_drives': total_drives,
        'active_drives': active_drives,
        'total_applications': total_applications,
        'selected': selected,
        'application_status': application_status,
        'top_companies': top_companies,
        'recent_applications': recent_applications,
    }

    return render(request, 'admin_dashboard.html', context)