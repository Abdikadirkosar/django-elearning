from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Course, Lesson, Enrollment, LessonProgress, Quiz, Question, Choice, Certificate
from accounts.models import Notification


class CoursesModelAndViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='teststudent',
            email='student@example.com',
            password='Password123'
        )
        self.admin_user = User.objects.create_superuser(
            username='testadmin',
            email='admin@example.com',
            password='AdminPassword123'
        )
        self.course = Course.objects.create(
            title='Python 101',
            description='Learn basic Python',
            instructor='John Doe',
            category='Programming',
            duration='3 Hours',
            price=0.00,
            is_published=True
        )
        self.lesson1 = Lesson.objects.create(
            course=self.course,
            title='Lesson 1: Intro',
            content='Hello Python',
            order=1,
            is_free_preview=True
        )
        self.lesson2 = Lesson.objects.create(
            course=self.course,
            title='Lesson 2: Variables',
            content='Variables guide',
            order=2,
            is_free_preview=False
        )

    def test_course_properties(self):
        self.assertEqual(self.course.total_lessons, 2)
        self.assertEqual(self.course.get_user_progress(self.user), 0)
        self.assertTrue(self.course.is_free)

    def test_home_page_status(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python 101')

    def test_course_list_status(self):
        response = self.client.get(reverse('course_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python 101')

    def test_course_detail_status(self):
        response = self.client.get(reverse('course_detail', kwargs={'pk': self.course.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lesson 1: Intro')

    def test_enrollment_workflow_free_course(self):
        self.client.login(username='teststudent', password='Password123')
        response = self.client.post(reverse('enroll_course', kwargs={'pk': self.course.id}))
        self.assertRedirects(response, reverse('course_detail', kwargs={'pk': self.course.id}))
        enrollment = Enrollment.objects.get(user=self.user, course=self.course)
        self.assertEqual(enrollment.status, 'approved')

    def test_paid_course_checkout_and_admin_approval(self):
        paid_course = Course.objects.create(
            title='Django Advanced',
            description='Deep dive Django',
            instructor='Eng. Abdikadir Kosar',
            category='Programming',
            duration='10 Hours',
            price=25.00,
            is_published=True
        )
        self.client.login(username='teststudent', password='Password123')

        # Clicking enroll on paid course redirects to checkout
        response = self.client.get(reverse('enroll_course', kwargs={'pk': paid_course.id}))
        self.assertRedirects(response, reverse('course_checkout', kwargs={'pk': paid_course.id}))

        # Submit checkout form
        post_data = {
            'payment_method': 'Zaad',
            'phone_number': '+252 63 4812030',
            'transaction_id': 'TXN-98214',
        }
        response = self.client.post(reverse('course_checkout', kwargs={'pk': paid_course.id}), post_data)
        self.assertRedirects(response, reverse('course_detail', kwargs={'pk': paid_course.id}))

        # Enrollment is created in 'pending' status
        enrollment = Enrollment.objects.get(user=self.user, course=paid_course)
        self.assertEqual(enrollment.status, 'pending')
        self.assertEqual(enrollment.transaction_id, 'TXN-98214')
        self.assertEqual(enrollment.amount_paid, 25.00)

        # Student gets a notification
        self.assertTrue(Notification.objects.filter(user=self.user, title__icontains='Dalabka').exists())

        # Now admin logs in and approves
        self.client.login(username='testadmin', password='AdminPassword123')
        approve_url = reverse('admin_panel_enrollment_approve', kwargs={'enrollment_id': enrollment.id})
        resp_approve = self.client.post(approve_url)
        self.assertRedirects(resp_approve, reverse('admin_panel_enrollments'))

        enrollment.refresh_from_db()
        self.assertEqual(enrollment.status, 'approved')
        self.assertIsNotNone(enrollment.approved_at)

        # Student received approval notification
        self.assertTrue(Notification.objects.filter(user=self.user, title__icontains='Fasaxay').exists())

    def test_free_preview_access(self):
        paid_course = Course.objects.create(
            title='AI Foundations',
            description='AI Guide',
            instructor='Eng. Abdikadir Kosar',
            category='AI',
            duration='5 Hours',
            price=30.00,
            is_published=True
        )
        preview_lesson = Lesson.objects.create(
            course=paid_course,
            title='AI Lesson 1 (Free Preview)',
            content='Welcome to AI',
            order=1,
            is_free_preview=True
        )
        locked_lesson = Lesson.objects.create(
            course=paid_course,
            title='AI Lesson 2 (Locked)',
            content='Advanced Neural Networks',
            order=2,
            is_free_preview=False
        )

        self.client.login(username='teststudent', password='Password123')

        # Student can view free preview lesson
        resp_preview = self.client.get(reverse('lesson_detail', kwargs={'pk': preview_lesson.id}))
        self.assertEqual(resp_preview.status_code, 200)
        self.assertContains(resp_preview, 'Free Preview')

        # Student cannot view locked lesson without approved enrollment
        resp_locked = self.client.get(reverse('lesson_detail', kwargs={'pk': locked_lesson.id}))
        self.assertRedirects(resp_locked, reverse('course_detail', kwargs={'pk': paid_course.id}))

    def test_lesson_completion(self):
        Enrollment.objects.create(user=self.user, course=self.course, status='approved')
        self.client.login(username='teststudent', password='Password123')

        response = self.client.post(reverse('complete_lesson', kwargs={'pk': self.lesson1.id}))
        self.assertTrue(LessonProgress.objects.filter(user=self.user, lesson=self.lesson1, completed=True).exists())
        self.assertEqual(self.course.get_user_progress(self.user), 50)

    def test_submit_review(self):
        Enrollment.objects.create(user=self.user, course=self.course, status='approved')
        self.client.login(username='teststudent', password='Password123')

        response = self.client.post(reverse('submit_review', kwargs={'pk': self.course.id}), {
            'rating': '5',
            'comment': 'Exceptional course!'
        })
        self.assertRedirects(response, reverse('course_detail', kwargs={'pk': self.course.id}))
        self.assertEqual(self.course.average_rating, 5.0)
        self.assertEqual(self.course.total_reviews, 1)

    def test_quiz_and_certificate(self):
        Enrollment.objects.create(user=self.user, course=self.course, status='approved')
        self.client.login(username='teststudent', password='Password123')

        quiz = Quiz.objects.create(course=self.course, title='Test Quiz', pass_percentage=70)
        q1 = Question.objects.create(quiz=quiz, text='Question 1', order=1)
        c1 = Choice.objects.create(question=q1, text='Correct Choice', is_correct=True)
        c2 = Choice.objects.create(question=q1, text='Wrong Choice', is_correct=False)

        # Submit quiz
        response = self.client.post(reverse('take_quiz', kwargs={'pk': self.course.id}), {
            f'question_{q1.id}': c1.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PASSED')

        # Certificate should be created
        self.assertTrue(Certificate.objects.filter(user=self.user, course=self.course).exists())
