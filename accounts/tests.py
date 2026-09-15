from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class AccountsTestCase(TestCase):
    def test_registration_success(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'Password123',
            'confirm_password': 'Password123'
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_registration_password_mismatch(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'Password123',
            'confirm_password': 'DifferentPassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Passwords do not match.')

    def test_login_logout(self):
        User.objects.create_user(username='john', email='john@example.com', password='MySecretPassword123')
        
        login_response = self.client.post(reverse('login'), {
            'username': 'john',
            'password': 'MySecretPassword123'
        })
        self.assertRedirects(login_response, reverse('dashboard'))

        logout_response = self.client.get(reverse('logout'))
        self.assertRedirects(logout_response, reverse('home'))
