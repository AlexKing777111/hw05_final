import shutil
import tempfile
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group, Comment


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


class PostViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="Stas")
        cls.group_1 = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.group_2 = Group.objects.create(
            title="Тестовая группа 2",
            slug="testslug_2",
            description="Тестовое описание 2",
        )
        cls.post_1 = Post.objects.create(
            author=cls.user,
            text="Тестовый текст1",
            group=cls.group_1,
            image="gif.jpg",
        )
        cls.comment = Comment.objects.create(
            post=cls.post_1, text="Комментарий", author=cls.user
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewTest.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон views."""
        templates_pages_names = {
            "posts/index.html": reverse("posts:index"),
            "posts/group_list.html": reverse(
                "posts:group_posts", kwargs={"slug": "test-slug"}
            ),
            "posts/profile.html": reverse(
                "posts:profile", kwargs={"username": "Stas"}
            ),
            "posts/post_detail.html": (
                reverse(
                    "posts:post_detail",
                    kwargs={"post_id": PostViewTest.post_1.pk},
                )
            ),
            "posts/post_create.html": reverse("posts:post_create"),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        """Шаблон главной страницы показывает правильный контекст."""
        response = self.guest_client.get(reverse("posts:index"))
        first_object = response.context["page_obj"][0]
        post_text = first_object.text
        post_image = first_object.image
        self.assertEqual(post_text, "Тестовый текст1")
        self.assertEqual(post_image, "gif.jpg")

    def test_group_page_show_correct_context(self):
        """Шаблон страницы групп показывает правильный контекст."""
        response = self.authorized_client.get(
            reverse("posts:group_posts", kwargs={"slug": "test-slug"})
        )
        first_object = response.context["page_obj"][0]
        post_group = first_object.group
        post_text = first_object.text
        post_image = first_object.image
        self.assertEqual(post_text, "Тестовый текст1")
        self.assertEqual(post_group, self.group_1)
        self.assertEqual(post_image, "gif.jpg")

    def test_profile_page_show_correct_context(self):
        """Шаблон страницы профиля показывает правильный контекст."""
        response = self.authorized_client.get(
            reverse("posts:profile", kwargs={"username": "Stas"})
        )
        first_object = response.context["page_obj"][0]
        post_author = first_object.author
        post_text = first_object.text
        post_image = first_object.image
        self.assertEqual(post_author, self.user)
        self.assertEqual(post_text, "Тестовый текст1")
        self.assertEqual(post_image, "gif.jpg")

    def test_post_detail_show_correct_context(self):
        """Шаблон страницы поста показывает правильный контекст."""
        response = self.authorized_client.get(
            reverse(
                "posts:post_detail", kwargs={"post_id": PostViewTest.post_1.pk}
            )
        )
        self.assertEqual(response.context["posts"].pk, PostViewTest.post_1.pk)
        self.assertEqual(response.context["posts"].image, "gif.jpg")

    def test_post_create_show_correct_context(self):
        """Шаблон создания поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
            "image": forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон редактирования поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                "posts:post_edit", kwargs={"post_id": PostViewTest.post_1.pk}
            )
        )
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
            "image": forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_comment(self):
        """Проверка добавления комментария к посту."""
        response = self.authorized_client.get(
            reverse(
                "posts:post_detail", kwargs={"post_id": PostViewTest.post_1.pk}
            )
        )
        self.assertEqual(len(response.context["comments"]), 1)

    def test_z_cache_home_page(self):
        """Тестируем удаление одной записи и отображение кеша"""
        response_predelete = self.guest_client.get(reverse("posts:index"))
        Post.objects.filter(pk=PostViewTest.post_1.pk).delete()
        response_deleted = self.guest_client.get(reverse("posts:index"))
        content_deleted = response_deleted.content
        self.assertEqual(response_predelete.content, content_deleted)
        cache.clear()
        response_cached = self.guest_client.get(reverse("posts:index"))
        content_cached = response_cached.content
        self.assertNotEqual(content_deleted, content_cached)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="Stas")
        cls.group_1 = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.group_2 = Group.objects.create(
            title="Тестовая группа 2",
            slug="testslug_2",
            description="Тестовое описание 2",
        )
        cls.posts_obj = []
        for i in range(50, 62):
            cls.posts_obj.append(
                Post(
                    author=cls.user,
                    text=f"{i} Тестовый пост",
                    group=cls.group_1,
                )
            )
        for i in range(62, 64):
            cls.posts_obj.append(
                Post(
                    author=cls.user,
                    text=f"{i} Тестовый пост",
                    group=cls.group_2,
                )
            )
        cls.posts_obj.append(Post(author=cls.user, text="88 Тестовый пост"))
        cls.posts = Post.objects.bulk_create(cls.posts_obj)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.user)

    def test_home_first_page_contains_ten_records(self):
        """Проверка паджинатора на главной странице."""
        response = self.guest_client.get(reverse("posts:index"))
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_home_second_page_contains_five_records(self):
        """Проверка паджинатора на главной второй странице."""
        response = self.guest_client.get(reverse("posts:index") + "?page=2")
        self.assertEqual(len(response.context["page_obj"]), 5)

    def test_group_first_page_contains_ten_records(self):
        """Проверка паджинатора на странице групп."""
        response = self.authorized_client.get(
            reverse("posts:group_posts", kwargs={"slug": "test-slug"})
        )
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_group_second_page_contains_two_records(self):
        """Проверка паджинатора на второй странице групп."""
        response = self.authorized_client.get(
            reverse("posts:group_posts", kwargs={"slug": "test-slug"})
            + "?page=2"
        )
        self.assertEqual(len(response.context["page_obj"]), 2)

    def test_profile_first_page_contains_ten_records(self):
        """Проверка паджинатора на первой странице профиля."""
        response = self.authorized_client.get(
            reverse("posts:profile", kwargs={"username": "Stas"})
        )
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_profile_second_page_contains_five_records(self):
        """Проверка паджинатора на второй странице профиля."""
        response = self.authorized_client.get(
            reverse("posts:profile", kwargs={"username": "Stas"}) + "?page=2"
        )
        self.assertEqual(len(response.context["page_obj"]), 5)
