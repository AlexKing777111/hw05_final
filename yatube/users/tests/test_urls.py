from django.contrib.auth import get_user_model
from http import HTTPStatus
from django.test import TestCase, Client

User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="Stas")

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_signup_url_at_desired_location(self):
        """Проверка доступности страницы регистрации."""
        response = self.guest_client.get("/auth/signup/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_url_at_desired_location(self):
        """Проверка доступности страницы выхода из аккаунта."""
        response = self.guest_client.get("/auth/logout/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_login_url_at_desired_location(self):
        """Проверка доступности страницы входа в аккаунт."""
        response = self.guest_client.get("/auth/login/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_url_at_desired_location(self):
        """Проверка доступности страницы смены пароля."""
        response = self.authorized_client.get("/auth/password_change/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_done_url_at_desired_location(self):
        """Проверка доступности страницы успешной смены пароля."""
        response = self.authorized_client.get("/auth/password_change/done/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_url_at_desired_location(self):
        """Проверка доступности страницы восстановления пароля."""
        response = self.authorized_client.get("/auth/password_reset/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_done_url_at_desired_location(self):
        """Проверка доступности страницы успешной отправки письма на почту."""
        response = self.authorized_client.get("/auth/password_reset/done/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_reset_done_url_at_desired_location(self):
        """Проверка доступности страницы успешной смены пароля."""
        response = self.authorized_client.get("/auth/reset/done/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_url_redirect_login(self):
        """Проверка редиректа."""
        response = self.guest_client.get("/auth/password_change/", follow=True)
        self.assertRedirects(
            response, "/auth/login/?next=/auth/password_change/"
        )
