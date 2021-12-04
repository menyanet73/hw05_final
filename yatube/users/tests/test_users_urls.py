from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from http import HTTPStatus

User = get_user_model()


class UserURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.user = User.objects.create_user(username='TestUser')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_users_urls(self):
        url_names = [
            reverse('users:signup'),
            reverse('users:login'),
            reverse('users:password_reset_form'),
            reverse('users:logout'),
        ]
        for url in url_names:
            with self.subTest(adress=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_users_urls_authorized(self):
        url_names = [
            reverse('users:signup'),
            reverse('users:login'),
            reverse('users:password_reset_form'),
            reverse('users:password_change'),
            reverse('users:password_change_done'),
            reverse('users:logout'),
        ]
        for url in url_names:
            with self.subTest(adress=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_users_url_redirect_anonymous(self):
        url_names = [
            reverse('users:password_change'),
            reverse('users:password_change_done'),
        ]
        for url in url_names:
            with self.subTest(adress=url):
                response = self.guest_client.get(url)
                self.assertRedirects(response, (f'/auth/login/?next={url}'))

    def test_users_urls_use_correct_templates(self):
        url_names = {
            'users/signup.html': reverse('users:signup'),
            'users/login.html': reverse('users:login'),
            'users/password_change.html': reverse('users:password_change'),
            'users/password_change_done.html':
                reverse('users:password_change_done'),
            'users/logged_out.html': reverse('users:logout'),
        }
        for template, url in url_names.items():
            with self.subTest(adress=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
