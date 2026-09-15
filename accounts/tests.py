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

    def test_user_profile_auto_created(self):
        user = User.objects.create_user(username='sarah', email='sarah@example.com', password='Password123')
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.role, 'student')

    def test_profile_view_get_and_update(self):
        user = User.objects.create_user(username='mike', email='mike@example.com', password='Password123')
        self.client.login(username='mike', password='Password123')

        # GET profile
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

        # POST update
        post_response = self.client.post(reverse('profile'), {
            'email': 'mike_new@example.com',
            'first_name': 'Michael',
            'last_name': 'Scott',
            'role': 'instructor',
            'headline': 'Regional Manager',
            'bio': 'World best boss',
            'phone': '123456789'
        })
        self.assertRedirects(post_response, reverse('profile'))
        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Michael')
        self.assertEqual(user.profile.role, 'instructor')

