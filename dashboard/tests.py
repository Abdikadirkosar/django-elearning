from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class DashboardTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='Password123'
        )

    def test_dashboard_unauthenticated_redirect(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_dashboard_authenticated_success(self):
        self.client.login(username='student1', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome, student1!')
