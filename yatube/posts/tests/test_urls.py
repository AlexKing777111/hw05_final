from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import Post, Group

User = get_user_model()


class PostUrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="Stas")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(author=cls.user, text="Тестовая текст")

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostUrlTest.user)

    def test_pages_urls_at_desired_location(self):
        """Проверка доступности страниц по ожидаемым адресам."""
        post = PostUrlTest.post
        url_names = {
            "/": HTTPStatus.OK,
            "/group/test-slug/": HTTPStatus.OK,
            "/profile/Stas/": HTTPStatus.OK,
            f"/posts/{post.pk}/": HTTPStatus.OK,
            "/create/": HTTPStatus.OK,
            f"/posts/{post.pk}/edit/": HTTPStatus.OK,
        }
        for url, status_code in url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_unexisting_page(self):
        """Проверка запроса к несуществующей странице."""
        response = self.authorized_client.get("/unexisting_page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_url_redirect_login(self):
        """Проверка редиректа создания поста."""
        response = self.guest_client.get("/create/", follow=True)
        self.assertRedirects(response, "/auth/login/?next=/create/")

    def test_edit_url_redirect_login(self):
        """Проверка редиректа редактирования поста."""
        post = PostUrlTest.post
        response = self.guest_client.get(
            f"/posts/{post.pk}/edit/", follow=True
        )
        self.assertRedirects(
            response, (f"/auth/login/?next=/posts/{post.pk}/edit/")
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        post = PostUrlTest.post
        templates_url_names = {
            "/": "posts/index.html",
            "/group/test-slug/": "posts/group_list.html",
            "/profile/Stas/": "posts/profile.html",
            f"/posts/{post.pk}/": "posts/post_detail.html",
            "/create/": "posts/post_create.html",
            f"/posts/{post.pk}/edit/": "posts/post_create.html",
            "/profile/Mama/": "core/404.html",
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
