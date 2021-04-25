from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get(reverse("posts:index"))
        self.assertEqual(response.status_code, 200)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        Group.objects.create(
            slug="test-slug",
        )
        Post.objects.create(
            id=1,
            text="Тест",
            author=User.objects.create_user(username="Test-user"),
        )

    def setUp(self) -> None:
        # неавторизованный клиент
        self.guest_client = Client()
        # авторизованный клиент
        self.user = User.objects.create_user(username="Andrey")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # автор
        self.author = User.objects.get(username="Test-user")
        self.author_client = Client()
        self.author_client.force_login(self.author)
        # список страниц
        self.templates_url_names = {
            "index.html": reverse("posts:index"),
            "group.html": reverse(
                "posts:group_post",
                kwargs={"slug": "test-slug"}
            ),
            "new_post.html": reverse("posts:new_post"),
            "follow.html": reverse("posts:follow_index"),
            "profile.html": reverse(
                "posts:profile",
                kwargs={"username": "Test-user"}
            ),
            "post.html": reverse(
                "posts:post",
                kwargs={"username": "Test-user", "post_id": 1}
            ),
        }

    def test_home_url(self):
        response = self.guest_client.get(reverse("posts:index"))
        self.assertEqual(response.status_code, 200)

    def test_group_posts_url(self):
        response = self.guest_client.get(reverse(
            "posts:group_post", kwargs={"slug": "test-slug"}))
        self.assertEqual(response.status_code, 200)

    def test_new_post_url_for_auth_user(self):
        response = self.authorized_client.get(reverse("posts:new_post"))
        self.assertEqual(response.status_code, 200)

    def test_url_new_post_use_correct_template(self):
        template_url_name = {
            "new_post.html": reverse(
                "posts:post_edit",
                kwargs={"username": "Test-user", "post_id": 1}
            ),
        }
        for template, url in template_url_name.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template(self):
        for template, url in self.templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_profile_url(self):
        response = self.guest_client.get(reverse(
            "posts:profile", kwargs={"username": "Test-user"}))
        self.assertEqual(response.status_code, 200)

    def test_post_for_watch_url(self):
        response = self.guest_client.get(reverse(
            "posts:post", kwargs={"username": "Test-user", "post_id": 1}))
        self.assertEqual(response.status_code, 200)

    def test_edit_post_for_author_url(self):
        response = self.author_client.get(reverse(
            "posts:post_edit", kwargs={"username": "Test-user", "post_id": 1}))
        self.assertEqual(response.status_code, 200)

    def test_edit_post_for_anon_url(self):
        response = self.guest_client.get(reverse(
            "posts:post_edit", kwargs={"username": "Test-user", "post_id": 1}))
        self.assertEqual(response.status_code, 302)

    def test_edit_post_for_authorized_url(self):
        response = self.authorized_client.get(reverse(
            "posts:post_edit", kwargs={"username": "Test-user", "post_id": 1})
        )
        self.assertRedirects(response, reverse(
            "posts:post", kwargs={"username": "Test-user", "post_id": 1}))

    def test_add_comment_for_anon_url(self):
        response = self.guest_client.get(reverse(
            "posts:add_comment",
            kwargs={"username": "Test-user", "post_id": 1})
        )
        self.assertRedirects(response, reverse("login"))
