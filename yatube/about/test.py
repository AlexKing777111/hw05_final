from http import HTTPStatus
from django.urls import reverse
from django.test import TestCase, Client


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_tech_url_at_desired_location(self):
        """Проверка доступности страницы технологий."""
        response = self.guest_client.get("/about/tech/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_url_at_desired_location(self):
        """Проверка доступности страницы автора."""
        response = self.guest_client.get("/about/author/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон views."""
        templates_pages_names = {
            "about/author.html": reverse("about:author"),
            "about/tech.html": reverse("about:tech"),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
