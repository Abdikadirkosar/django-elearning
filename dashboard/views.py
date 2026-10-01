from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from courses.models import Enrollment, LessonProgress, Lesson


@login_required
def dashboard_view(request):
    user = request.user
    enrollments = Enrollment.objects.filter(user=user).select_related('course').order_by('-enrolled_at')
    
    active_courses_data = []
    completed_courses_data = []
    pending_courses_data = []
    rejected_courses_data = []

    total_completed_lessons = LessonProgress.objects.filter(user=user, completed=True).count()
    completed_courses_count = 0
    total_possible_lessons = 0

    for enrollment in enrollments:
        course = enrollment.course

        if enrollment.status == 'pending':
            pending_courses_data.append({
                'enrollment': enrollment,
                'course': course,
                'transaction_id': enrollment.transaction_id,
                'payment_method': enrollment.payment_method,
                'amount_paid': enrollment.amount_paid or course.price,
                'enrolled_at': enrollment.enrolled_at,
            })
            continue

        if enrollment.status == 'rejected':
            rejected_courses_data.append({
                'enrollment': enrollment,
                'course': course,
                'admin_notes': enrollment.admin_notes,
                'enrolled_at': enrollment.enrolled_at,
            })
            continue

        # Approved / Active Courses
        progress_pct = course.get_user_progress(user)
        c_lessons_count = course.lessons.count()
        total_possible_lessons += c_lessons_count

        if progress_pct == 100 and c_lessons_count > 0:
            completed_courses_count += 1

        # Find the next uncompleted lesson, or the first lesson
        completed_lesson_ids = LessonProgress.objects.filter(
            user=user, lesson__course=course, completed=True
        ).values_list('lesson_id', flat=True)

        next_lesson = course.lessons.exclude(id__in=completed_lesson_ids).order_by('order', 'id').first()
        if not next_lesson:
            next_lesson = course.lessons.order_by('order', 'id').first()

        item_data = {
            'enrollment': enrollment,
            'course': course,
            'progress': progress_pct,
            'total_lessons': c_lessons_count,
            'next_lesson': next_lesson,
            'enrolled_at': enrollment.enrolled_at,
        }

        if progress_pct == 100:
            completed_courses_data.append(item_data)
        else:
            active_courses_data.append(item_data)

    overall_progress = 0
    if total_possible_lessons > 0:
        overall_progress = int((total_completed_lessons / total_possible_lessons) * 100)

    context = {
        'active_courses_data': active_courses_data,
        'completed_courses_data': completed_courses_data,
        'pending_courses_data': pending_courses_data,
        'rejected_courses_data': rejected_courses_data,
        'enrolled_count': len(active_courses_data) + len(completed_courses_data),
        'pending_count': len(pending_courses_data),
        'completed_lessons_count': total_completed_lessons,
        'overall_progress': overall_progress,
        'certificates_count': completed_courses_count,
    }
    return render(request, 'dashboard/dashboard.html', context)

