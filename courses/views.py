from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.contrib.auth.models import User
from .models import Course, Lesson, Enrollment, LessonProgress


def home(request):
    featured_courses = Course.objects.filter(is_published=True)[:3]
    total_courses = Course.objects.filter(is_published=True).count()
    total_students = User.objects.filter(enrollments__isnull=False).distinct().count()
    total_lessons = Lesson.objects.filter(course__is_published=True).count()

    context = {
        'featured_courses': featured_courses,
        'total_courses': total_courses,
        'total_students': total_students,
        'total_lessons': total_lessons,
    }
    return render(request, 'courses/home.html', context)


def course_list(request):
    courses = Course.objects.filter(is_published=True)
    categories = Course.objects.filter(is_published=True).values_list('category', flat=True).distinct()

    search_query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', '').strip()

    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(instructor__icontains=search_query)
        )

    if selected_category:
        courses = courses.filter(category__iexact=selected_category)

    context = {
        'courses': courses,
        'categories': categories,
        'search_query': search_query,
        'selected_category': selected_category,
    }
    return render(request, 'courses/course_list.html', context)


def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk, is_published=True)
    lessons = course.lessons.all()
    
    is_enrolled = False
    progress = 0
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
        if is_enrolled:
            progress = course.get_user_progress(request.user)

    context = {
        'course': course,
        'lessons': lessons,
        'is_enrolled': is_enrolled,
        'progress': progress,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def enroll_course(request, pk):
    if request.method != 'POST':
        return redirect('course_detail', pk=pk)

    course = get_object_or_404(Course, pk=pk, is_published=True)
    enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)

    if created:
        messages.success(request, f"You have successfully enrolled in '{course.title}'.")
    else:
        messages.info(request, f"You are already enrolled in '{course.title}'.")

    return redirect('course_detail', pk=course.id)


@login_required
def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    course = lesson.course

    # Check if user is enrolled in the course
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    if not is_enrolled:
        messages.error(request, "Please enroll in this course to access lessons.")
        return redirect('course_detail', pk=course.id)

    # Next and previous lessons
    prev_lesson = Lesson.objects.filter(course=course, order__lt=lesson.order).order_by('-order', '-id').first()
    next_lesson = Lesson.objects.filter(course=course, order__gt=lesson.order).order_by('order', 'id').first()

    is_completed = LessonProgress.objects.filter(
        user=request.user, lesson=lesson, completed=True
    ).exists()

    context = {
        'lesson': lesson,
        'course': course,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'is_completed': is_completed,
    }
    return render(request, 'courses/lesson_detail.html', context)


@login_required
def complete_lesson(request, pk):
    if request.method != 'POST':
        return redirect('lesson_detail', pk=pk)

    lesson = get_object_or_404(Lesson, pk=pk)
    course = lesson.course

    # Ensure user is enrolled
    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.error(request, "You must be enrolled to complete lessons.")
        return redirect('course_detail', pk=course.id)

    progress, created = LessonProgress.objects.get_or_create(
        user=request.user, lesson=lesson
    )
    progress.completed = True
    progress.save()

    messages.success(request, f"Lesson '{lesson.title}' marked as completed.")

    # Redirect to next lesson if available, else stay on current lesson
    next_lesson = Lesson.objects.filter(course=course, order__gt=lesson.order).order_by('order', 'id').first()
    if next_lesson:
        return redirect('lesson_detail', pk=next_lesson.id)
    return redirect('lesson_detail', pk=lesson.id)


def custom_404_view(request, exception):
    return render(request, '404.html', status=404)


def custom_500_view(request):
    return render(request, '500.html', status=500)
