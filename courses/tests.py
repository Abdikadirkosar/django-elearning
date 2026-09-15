from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Course, Lesson, Enrollment, LessonProgress


class CoursesModelAndViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='teststudent',
            email='student@example.com',
            password='Password123'
        )
        self.course = Course.objects.create(
            title='Python 101',
            description='Learn basic Python',
            instructor='John Doe',
            category='Programming',
            duration='3 Hours',
            is_published=True
        )
        self.lesson1 = Lesson.objects.create(
            course=self.course,
            title='Lesson 1: Intro',
            content='Hello Python',
            order=1
        )
        self.lesson2 = Lesson.objects.create(
            course=self.course,
            title='Lesson 2: Variables',
            content='Variables guide',
            order=2
        )

    def test_course_properties(self):
        self.assertEqual(self.course.total_lessons, 2)
        self.assertEqual(self.course.get_user_progress(self.user), 0)

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

    def test_enrollment_workflow(self):
        self.client.login(username='teststudent', password='Password123')
        response = self.client.post(reverse('enroll_course', kwargs={'pk': self.course.id}))
        self.assertRedirects(response, reverse('course_detail', kwargs={'pk': self.course.id}))
        self.assertTrue(Enrollment.objects.filter(user=self.user, course=self.course).exists())

    def test_lesson_completion(self):
        Enrollment.objects.create(user=self.user, course=self.course)
        self.client.login(username='teststudent', password='Password123')

        response = self.client.post(reverse('complete_lesson', kwargs={'pk': self.lesson1.id}))
        self.assertTrue(LessonProgress.objects.filter(user=self.user, lesson=self.lesson1, completed=True).exists())

        # Progress should now be 50%
        self.assertEqual(self.course.get_user_progress(self.user), 50)
