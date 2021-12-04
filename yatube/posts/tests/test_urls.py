from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

from http import HTTPStatus

User = get_user_model()


class StaticURLTests(TestCase):
    def test_static_pages(self):
        reverse_names = [
            reverse('posts:index'),
            reverse('about:author'),
            reverse('about:tech'),
        ]
        for reverse_name in reverse_names:
            with self.subTest(adress=reverse_name):
                cache.clear()
                response = self.client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='TestAuthor')
        User.objects.create(username='TestNoAuthor')
        Group.objects.create(
            title='Test group',
            slug='test_group',
            description='Test group',
        )
        cls.post = Post.objects.create(
            text='Test post',
            author=cls.user,
            group=Group.objects.get(slug='test_group'),
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_exists_at_desired_location(self):
        reverse_names = [
            reverse('posts:group_list', kwargs={'slug': self.post.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user}),
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
        ]
        for reverse_name in reverse_names:
            with self.subTest(adress=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exists_at_desired_location_authorized(self):
        reverse_names = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
        ]
        for reverse_name in reverse_names:
            with self.subTest(adress=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_redirect_anonymous(self):
        reverses = {
            'create': reverse('posts:post_create'),
            'edit': reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            )
        }
        reverse_names = {
            reverses['create']:
                reverse('users:login') + f'?next={reverses["create"]}',
            reverses['edit']:
                reverse('users:login') + f'?next={reverses["edit"]}',
        }
        for url, redirect_url in reverse_names.items():
            with self.subTest(adress=url):
                response = self.client.get(url)
                self.assertRedirects(response, (redirect_url))

    def test_edit_url_redirect_not_author(self):
        self.reader = User.objects.get(username='TestNoAuthor')
        self.reader_client = Client()
        self.reader_client.force_login(self.reader)
        response = self.reader_client.get(f'/posts/{self.post.id}/edit/')
        self.assertRedirects(response, (f'/posts/{self.post.id}/'))

    def test_not_existing_url(self):
        response = self.client.get('/not_existing_url/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_templates(self):
        reverse_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.post.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.post.author}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                'posts/create_post.html',
        }
        for reverse_name, template in reverse_names.items():
            with self.subTest(adress=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
