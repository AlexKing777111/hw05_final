from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="Тестовый слаг",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовая текст",
        )

    def test_models_str_group(self):
        """Проверка корректной работы __str__ у моделей групп."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_models_str_post(self):
        """Проверка корректной работы __str__ у моделей постов."""
        post = PostModelTest.post
        expected_object_name = post.text
        self.assertEqual(expected_object_name, str(post))

    def test_help_text_post_matches_the_expected(self):
        """Проверка help_text."""
        post = PostModelTest.post
        help_text_text = post._meta.get_field("text").help_text
        help_text_group = post._meta.get_field("group").help_text
        self.assertEqual(help_text_text, "Текст нового поста")
        self.assertEqual(
            help_text_group, "Группа, к которой будет относиться пост"
        )

    def test_verbose_name_post(self):
        """verbose_name в post в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            "pub_date": "Дата публикации",
            "text": "Текст поста",
            "author": "Автор",
            "group": "Группа",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_verbose_name_group(self):
        """verbose_name в group в полях совпадает с ожидаемым."""
        group = PostModelTest.group
        field_verboses = {
            "title": "Название",
            "description": "Описание",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value
                )
