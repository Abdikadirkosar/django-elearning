from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from functools import wraps

from courses.models import Course, Enrollment, LessonProgress, Certificate, QuizAttempt, Quiz
from accounts.models import UserProfile, Notification
from accounts.forms import UserLoginForm


# ─── Admin Login Page ─────────────────────────────────────────────────────────
def admin_login_view(request):
    """Dedicated beautiful admin login page."""
    if request.user.is_authenticated:
        try:
            if request.user.is_superuser or request.user.profile.role == 'admin':
                return redirect('admin_panel_dashboard')
        except Exception:
            if request.user.is_superuser:
                return redirect('admin_panel_dashboard')
        return redirect('dashboard')
    form = UserLoginForm()
    return render(request, 'admin_panel/admin_login.html', {'form': form})



# ─── Admin Required Decorator ────────────────────────────────────────────────
def admin_required(view_func):
    """Only allow superusers or users with role='admin'."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            is_admin = request.user.is_superuser or request.user.profile.role == 'admin'
        except Exception:
            is_admin = request.user.is_superuser
        if not is_admin:
            messages.error(request, "Access denied. Admin privileges required.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# ─── Dashboard ────────────────────────────────────────────────────────────────
@admin_required
def admin_dashboard(request):
    total_users = User.objects.count()
    total_courses = Course.objects.count()
    total_enrollments = Enrollment.objects.count()
    pending_enrollments = Enrollment.objects.filter(status='pending').count()
    approved_enrollments = Enrollment.objects.filter(status='approved').count()
    total_certificates = Certificate.objects.count()

    students = User.objects.filter(profile__role='student').count()
    instructors = User.objects.filter(profile__role='instructor').count()
    admins = User.objects.filter(profile__role='admin').count()

    published_courses = Course.objects.filter(is_published=True).count()
    unpublished_courses = Course.objects.filter(is_published=False).count()

    recent_enrollments = Enrollment.objects.select_related('user', 'course').order_by('-enrolled_at')[:8]
    recent_users = User.objects.order_by('-date_joined')[:8]

    context = {
        'total_users': total_users,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'pending_enrollments': pending_enrollments,
        'approved_enrollments': approved_enrollments,
        'total_certificates': total_certificates,
        'students': students,
        'instructors': instructors,
        'admins': admins,
        'published_courses': published_courses,
        'unpublished_courses': unpublished_courses,
        'recent_enrollments': recent_enrollments,
        'recent_users': recent_users,
    }
    return render(request, 'admin_panel/dashboard.html', context)


# ─── Users ────────────────────────────────────────────────────────────────────
@admin_required
def admin_users(request):
    role_filter = request.GET.get('role', '')
    search = request.GET.get('search', '')

    users = User.objects.select_related('profile').order_by('-date_joined')
    if role_filter:
        users = users.filter(profile__role=role_filter)
    if search:
        users = users.filter(username__icontains=search) | users.filter(email__icontains=search)

    context = {
        'users': users,
        'role_filter': role_filter,
        'search': search,
        'total': users.count(),
    }
    return render(request, 'admin_panel/users.html', context)


@admin_required
def admin_user_role_change(request, user_id):
    """Change a user's role (POST only)."""
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id)
        new_role = request.POST.get('role')
        if new_role in ['student', 'instructor', 'admin']:
            profile, _ = UserProfile.objects.get_or_create(user=target_user)
            profile.role = new_role
            profile.save()
            messages.success(request, f"{target_user.username} role changed to {new_role}.")
        else:
            messages.error(request, "Invalid role selected.")
    return redirect('admin_panel_users')


@admin_required
def admin_user_delete(request, user_id):
    """Delete a user (POST only). Cannot delete yourself."""
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id)
        if target_user == request.user:
            messages.error(request, "You cannot delete your own account.")
        else:
            username = target_user.username
            target_user.delete()
            messages.success(request, f"User '{username}' has been deleted.")
    return redirect('admin_panel_users')


# ─── Courses ──────────────────────────────────────────────────────────────────
@admin_required
def admin_courses(request):
    search = request.GET.get('search', '')
    courses = Course.objects.annotate(enroll_count=Count('enrollments')).order_by('-created_at')
    if search:
        courses = courses.filter(title__icontains=search)

    context = {
        'courses': courses,
        'search': search,
        'total': courses.count(),
    }
    return render(request, 'admin_panel/courses.html', context)


@admin_required
def admin_course_add(request):
    from courses.forms import CourseForm
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Course created successfully!")
            return redirect('admin_panel_courses')
    else:
        form = CourseForm()
    return render(request, 'admin_panel/course_form.html', {'form': form, 'action': 'Add'})


@admin_required
def admin_course_edit(request, course_id):
    from courses.forms import CourseForm
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f"Course '{course.title}' updated!")
            return redirect('admin_panel_courses')
    else:
        form = CourseForm(instance=course)
    return render(request, 'admin_panel/course_form.html', {'form': form, 'action': 'Edit', 'course': course})


@admin_required
def admin_course_delete(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        title = course.title
        course.delete()
        messages.success(request, f"Course '{title}' has been deleted.")
    return redirect('admin_panel_courses')


@admin_required
def admin_course_toggle_publish(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        course.is_published = not course.is_published
        course.save()
        status = "published" if course.is_published else "unpublished"
        messages.success(request, f"Course '{course.title}' is now {status}.")
    return redirect('admin_panel_courses')


# ─── Enrollments ──────────────────────────────────────────────────────────────
@admin_required
def admin_enrollments(request):
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')

    enrollments = Enrollment.objects.select_related('user', 'course').order_by('-enrolled_at')
    
    pending_count = Enrollment.objects.filter(status='pending').count()
    approved_count = Enrollment.objects.filter(status='approved').count()
    rejected_count = Enrollment.objects.filter(status='rejected').count()

    if status_filter:
        enrollments = enrollments.filter(status=status_filter)
    if search:
        enrollments = enrollments.filter(
            Q(user__username__icontains=search) |
            Q(course__title__icontains=search) |
            Q(transaction_id__icontains=search)
        )

    context = {
        'enrollments': enrollments,
        'search': search,
        'status_filter': status_filter,
        'total': enrollments.count(),
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }
    return render(request, 'admin_panel/enrollments.html', context)


@admin_required
def admin_enrollment_approve(request, enrollment_id):
    if request.method == 'POST':
        enrollment = get_object_or_404(Enrollment, id=enrollment_id)
        enrollment.status = 'approved'
        enrollment.approved_at = timezone.now()
        enrollment.save()

        # Send in-app notification to student
        Notification.objects.create(
            user=enrollment.user,
            title="🎉 Koorsadaadii Waa La Fasaxay!",
            message=f"Hambalyo! Dalabkaagii koorsada '{enrollment.course.title}' waa la ansixiyay. Hadda waad bilaabi kartaa dhammaan casharrada.",
            link=reverse('course_detail', kwargs={'pk': enrollment.course.id})
        )

        messages.success(request, f"Dalabka ardayga '{enrollment.user.username}' ee koorsada '{enrollment.course.title}' si guul leh ayaa loo fasaxay (Approved)!")
    return redirect('admin_panel_enrollments')


@admin_required
def admin_enrollment_reject(request, enrollment_id):
    if request.method == 'POST':
        enrollment = get_object_or_404(Enrollment, id=enrollment_id)
        enrollment.status = 'rejected'
        reason = request.POST.get('reason', '').strip()
        if reason:
            enrollment.admin_notes = reason
        enrollment.save()

        # Send in-app notification to student
        msg_text = f"Nasiib-darro, dalabkaagii koorsada '{enrollment.course.title}' lama ansixin."
        if reason:
            msg_text += f" Sababta: {reason}."
        msg_text += " Fadlan la soo xiriir xafiiska taageerada (+252 634812030)."

        Notification.objects.create(
            user=enrollment.user,
            title="Codsigaaga Koorsada Lama Ansixin",
            message=msg_text,
            link=reverse('contact')
        )

        messages.warning(request, f"Dalabka '{enrollment.user.username}' waa la diiday (Rejected).")
    return redirect('admin_panel_enrollments')


# ─── Certificates ─────────────────────────────────────────────────────────────
@admin_required
def admin_certificates(request):
    certificates = Certificate.objects.select_related('user', 'course').order_by('-issued_at')
    search = request.GET.get('search', '')
    if search:
        certificates = certificates.filter(user__username__icontains=search) | \
                       certificates.filter(course__title__icontains=search)
    context = {'certificates': certificates, 'search': search, 'total': certificates.count()}
    return render(request, 'admin_panel/certificates.html', context)


# ─── Quiz Attempts ────────────────────────────────────────────────────────────
@admin_required
def admin_quizzes(request):
    attempts = QuizAttempt.objects.select_related('user', 'quiz', 'quiz__course').order_by('-completed_at')
    search = request.GET.get('search', '')
    if search:
        attempts = attempts.filter(user__username__icontains=search) | \
                   attempts.filter(quiz__course__title__icontains=search)
    context = {'attempts': attempts, 'search': search, 'total': attempts.count()}
    return render(request, 'admin_panel/quizzes.html', context)
