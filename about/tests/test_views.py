from django.test import Client, TestCase
from django.urls import reverse


class AboutPagesTests(TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        template_page_names = {
            "author.html": reverse("about:author"),
            "tech.html": reverse("about:tech"),
        }
        for template, reverse_name in template_page_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_about_author_page(self):
        response = self.guest_client.get(reverse("about:author"))
        self.assertEqual(response.status_code, 200)

    def test_about_tech_page(self):
        response = self.guest_client.get(reverse("about:tech"))
        self.assertEqual(response.status_code, 200)
