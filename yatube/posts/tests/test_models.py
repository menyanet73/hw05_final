from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='тесты' * 4,
        )

    def test_model_have_correct_objects_names(self):
        text = self.post.text[:15]
        self.assertEqual(str(self.post), text)

    def test_post_model_help_text(self):
        field_help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост'
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )

    def test_model_have_correct_objects_names(self):
        self.assertEqual(str(self.group), self.group.title)

    def test_group_model_help_text(self):
        field_help_texts = {
            'title': 'введите название группы, не более 200 символов',
            'slug': 'ссылка должна состоять из цифр,'
                    ' букв и нижних подчеркиваний',
            'description': 'введите текстовое описание группы'
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field).help_text,
                    expected_value
                )
