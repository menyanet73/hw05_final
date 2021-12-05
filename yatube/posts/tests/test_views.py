import shutil
import tempfile
from datetime import datetime

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse
from posts.models import Comment, Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='TestUser')
        cls.user2 = User.objects.create(username='TestUser2')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test_group',
            description='Test group',
        )
        cls.group2 = Group.objects.create(
            title='Group not for posts',
            slug='not_group',
            description='Test not group',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_posts_pages_uses_correct_templates(self):
        template_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',

        }
        for reverse_name, template in template_names.items():
            with self.subTest(adress=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_page_obj_show_correct_context(self):
        response_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for response_name in response_names:
            with self.subTest(adress=response_name):
                response = self.authorized_client.get(response_name)
                post = response.context['page_obj'][0]
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.author, self.user)
                self.assertEqual(post.group, self.group)
                self.assertEqual(post.created.date(), datetime.today().date())

    def test_post_detail_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        post = response.context['post']
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.created.date(), datetime.today().date())

    def test_context_without_posts(self):
        reverse_names = [
            reverse('posts:group_list', kwargs={'slug': self.group2.slug}),
            reverse('posts:profile', kwargs={'username': self.user2.username}),
        ]
        for reverse_name in reverse_names:
            with self.subTest(adress=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 0)

    def test_form_pages_show_correct_context(self):
        response_names = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        ]
        for response_name in response_names:
            response = self.authorized_client.get(response_name)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='TestUser')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test_group',
            description='Test group',
        )
        for i in range(1, settings.PAGE_COUNT + 4):
            Post.objects.create(
                author=cls.user,
                text=f'{i}st Post',
                group=cls.group,
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_two_pages_contains_posts(self):
        reverse_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
        ]
        for reverse_name in reverse_names:
            with self.subTest(adress=reverse_name):
                response = self.authorized_client.get(reverse_name)
                resp2 = self.authorized_client.get(reverse_name + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    settings.PAGE_COUNT
                )
                self.assertEqual(len(resp2.context['page_obj']), 3)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImagePostViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="Test")
        cls.group = Group.objects.create(
            title='TestGroup',
            slug='test_image_group',
            description='Test group'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='',
            author=cls.user,
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_image_post_on_pages(self):
        reverse_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user}),
        ]
        for reverse_name in reverse_names:
            with self.subTest(adress=reverse_name):
                response = self.authorized_client.get(reverse_name)
                post = response.context['page_obj'][0]
                self.assertEqual(post.image, 'posts/small.gif')

    def test_image_post_on_post_detail(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        post = response.context['post']
        self.assertEqual(post.image, 'posts/small.gif')


class CommentsPostTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='CommentUser')
        cls.post = Post.objects.create(
            text='',
            author=cls.user,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_non_authorized_client_cant_comment(self):
        comments_count = Comment.objects.count()
        reverse_name = reverse(
            'posts:add_comment', kwargs={'post_id': self.post.id}
        )
        form_data = {
            'text': 'TestComment'
        }
        response = self.client.post(
            reverse_name,
            form_data,
        )
        self.assertRedirects(
            response, reverse('users:login') + '?next=' + reverse_name
        )
        self.assertEqual(comments_count, Comment.objects.count())

    def test_authorized_client_can_comment(self):
        comments_count = Comment.objects.count()
        reverse_name = reverse(
            'posts:add_comment', kwargs={'post_id': self.post.id}
        )
        form_data = {
            'text': 'TestComment'
        }
        response = self.authorized_client.post(
            reverse_name,
            form_data,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)

    def test_comment_on_post_page(self):
        reverse_name = reverse(
            'posts:add_comment', kwargs={'post_id': self.post.id}
        )
        form_data = {
            'text': 'TestComment'
        }
        self.authorized_client.post(
            reverse_name,
            form_data,
        )
        response = self.client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        comments = response.context['comments']
        self.assertEqual(comments[0].text, form_data['text'])


class CacheTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='TestCacheUser')
        cls.post = Post.objects.create(
            text='Test post, for test cache in index page.',
            author=cls.user,
        )

    def test_cache_index(self):
        response = self.client.get(reverse('posts:index'))
        content = response.content
        self.assertIn(self.post, response.context['page_obj'])
        self.post.delete()
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(content, response.content)
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertNotEqual(content, response.content)


class FollowTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='TestFollowAuthor')
        cls.follower = User.objects.create(username='TestFollower')
        cls.not_follower = User.objects.create(username='TestNotFollower')
        cls.post = Post.objects.create(
            text='Test post for follower',
            author=cls.author,
        )

    def setUp(self):
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)
        self.not_follower_client = Client()
        self.not_follower_client.force_login(self.not_follower)

    def test_create_follow(self):
        self.follower_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.author})
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.follower,
                author=self.author
            ).exists()
        )

    def test_delete_follow(self):
        Follow.objects.create(user=self.follower, author=self.author)
        self.follower_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': self.author})
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.follower,
                author=self.author
            ).exists()
        )

    def test_follow_page_context(self):
        Follow.objects.create(
            author=self.author,
            user=self.follower,
        )
        reverse_name = reverse('posts:follow_index')
        response_follower = self.follower_client.get(reverse_name)
        response_not_follower = self.not_follower_client.get(reverse_name)
        self.assertEqual(response_follower.context['page_obj'][0], self.post)
        self.assertNotEqual(len(response_not_follower.context), 0)
