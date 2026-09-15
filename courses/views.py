from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.contrib.auth.models import User
from .models import Course, Lesson, Enrollment, LessonProgress, Review, Quiz, Question, Choice, QuizAttempt, Certificate



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
    reviews = course.reviews.select_related('user').all()
    
    is_enrolled = False
    progress = 0
    user_review = None
    certificate = None
    quiz = getattr(course, 'quiz', None)
    latest_attempt = None

    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
        if is_enrolled:
            progress = course.get_user_progress(request.user)
            user_review = reviews.filter(user=request.user).first()
            certificate = Certificate.objects.filter(user=request.user, course=course).first()
            if quiz:
                latest_attempt = QuizAttempt.objects.filter(user=request.user, quiz=quiz).first()

    context = {
        'course': course,
        'lessons': lessons,
        'reviews': reviews,
        'is_enrolled': is_enrolled,
        'progress': progress,
        'user_review': user_review,
        'certificate': certificate,
        'quiz': quiz,
        'latest_attempt': latest_attempt,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def submit_review(request, pk):
    if request.method != 'POST':
        return redirect('course_detail', pk=pk)

    course = get_object_or_404(Course, pk=pk, is_published=True)

    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.error(request, "You must be enrolled in this course to leave a review.")
        return redirect('course_detail', pk=course.id)

    try:
        rating = int(request.POST.get('rating', 5))
        if rating < 1 or rating > 5:
            rating = 5
    except (ValueError, TypeError):
        rating = 5

    comment = request.POST.get('comment', '').strip()
    if not comment:
        messages.error(request, "Please write a comment for your review.")
        return redirect('course_detail', pk=course.id)

    Review.objects.update_or_create(
        course=course,
        user=request.user,
        defaults={'rating': rating, 'comment': comment}
    )

    messages.success(request, "Thank you! Your course review has been submitted.")
    return redirect('course_detail', pk=course.id)


@login_required
def take_quiz(request, pk):
    course = get_object_or_404(Course, pk=pk, is_published=True)

    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.error(request, "You must enroll in this course to take the quiz.")
        return redirect('course_detail', pk=course.id)

    quiz = getattr(course, 'quiz', None)
    if not quiz:
        messages.info(request, "No quiz has been added to this course yet.")
        return redirect('course_detail', pk=course.id)

    questions = quiz.questions.prefetch_related('choices').all()

    if request.method == 'POST':
        total_q = questions.count()
        correct_q = 0

        for q in questions:
            choice_id = request.POST.get(f'question_{q.id}')
            if choice_id:
                if Choice.objects.filter(id=choice_id, question=q, is_correct=True).exists():
                    correct_q += 1

        score = int((correct_q / total_q) * 100) if total_q > 0 else 0
        passed = score >= quiz.pass_percentage

        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            score=score,
            passed=passed
        )

        if passed:
            cert, created = Certificate.objects.get_or_create(user=request.user, course=course)
            if created:
                messages.success(request, f"🎉 Congratulations! You scored {score}% and earned your Certificate of Completion!")
            else:
                messages.success(request, f"Great job! You passed the quiz with {score}%.")
        else:
            messages.warning(request, f"You scored {score}%. The passing mark is {quiz.pass_percentage}%. You can retake the quiz anytime.")

        return render(request, 'courses/quiz_result.html', {
            'course': course,
            'quiz': quiz,
            'attempt': attempt,
            'score': score,
            'passed': passed,
            'total_q': total_q,
            'correct_q': correct_q,
        })

    latest_attempt = QuizAttempt.objects.filter(user=request.user, quiz=quiz).first()
    return render(request, 'courses/quiz.html', {
        'course': course,
        'quiz': quiz,
        'questions': questions,
        'latest_attempt': latest_attempt,
    })


@login_required
def view_certificate(request, pk):
    course = get_object_or_404(Course, pk=pk, is_published=True)

    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.error(request, "You must be enrolled to view certificates.")
        return redirect('course_detail', pk=course.id)

    cert = Certificate.objects.filter(user=request.user, course=course).first()
    
    # If not yet awarded, award it if course progress is 100%
    if not cert:
        if course.get_user_progress(request.user) >= 100:
            cert = Certificate.objects.create(user=request.user, course=course)
            messages.success(request, "🎉 Congratulations! Course completed and certificate generated!")
        else:
            messages.info(request, "Complete all lessons or pass the course quiz to earn your Certificate.")
            return redirect('course_detail', pk=course.id)

    return render(request, 'courses/certificate.html', {
        'course': course,
        'certificate': cert,
    })



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
