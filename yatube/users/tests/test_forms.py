from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class CreateUserTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_create_new_user(self):
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Arthur',
            'last_name': 'Kingovsky',
            'username': 'KingArthur',
            'email': 'KingArthur@rambler.com',
            'password1': 'arthur123sobaka',
            'password2': 'arthur123sobaka',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertRedirects(response, reverse('posts:index'))
        self.assertTrue(
            User.objects.filter(
                username='KingArthur'
            )
        )
