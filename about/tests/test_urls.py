from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.templates_url_names = {
            "author.html": "/about/author/",
            "tech.html": "/about/tech/",
        }

    def test_about_author_page(self):
        response = self.guest_client.get(reverse("about:author"))
        self.assertEqual(response.status_code, 200)

    def test_about_tech_page(self):
        response = self.guest_client.get(reverse("about:tech"))
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        for template, url in self.templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
