from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="Stas")

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_user_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон views."""
        templates_pages_names = {
            "users/signup.html": reverse("users:signup"),
            "users/logged_out.html": reverse("users:logout"),
            "users/login.html": reverse("users:login"),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
