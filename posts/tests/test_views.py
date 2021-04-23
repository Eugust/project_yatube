import shutil
import tempfile
import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django import forms
import time

from posts.models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.test_group = Group.objects.create(
            title="Тестовая группа", slug="test-slug"
        )
        cls.test_author = User.objects.create_user(
            username="Автор"
        )
        cls.test_group_2 = Group.objects.create(
            title="Дополнительная группа", slug="test-slug-2"
        )
        cls.posts = []
        for num in range(10):
            time.sleep(0.01)
            cls.posts.append(
                Post(
                    text=f"Пост {num+1}",
                    author=cls.test_author,
                    group=cls.test_group,
                )
            )
        Post.objects.bulk_create(cls.posts)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self) -> None:
        self.guest_client = Client()
        self.user = User.objects.create_user(username="Andrey")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.test_author)
        self.image = SimpleUploadedFile(
            name="test_image.gif",
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00',
            content_type="image/gif",
        )
        Post.objects.create(
            text="Пост",
            author=PostPagesTests.test_author,
            group=PostPagesTests.test_group,
            image=self.image
        )

    def test_pages_uses_correct_template(self):
        template_page_names = {
            "index.html": reverse("posts:index"),
            "new_post.html": reverse("posts:new_post"),
            "group.html": (
                reverse("posts:group_post", kwargs={"slug": "test-slug"})
            ),
        }
        for template, reverse_name in template_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        response = self.guest_client.get(reverse("posts:index"))
        first_object = response.context.get("page").object_list[0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_author_0 = first_object.author.username
        self.assertEqual(post_text_0, "Пост")
        self.assertEqual(post_group_0, self.test_group.title)
        self.assertEqual(post_author_0, self.test_author.username)
        self.assertTrue(
            re.fullmatch(r"posts/test_image.*\.gif", "posts/test_image.gif")
        )

    def test_group_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            "posts:group_post",
            kwargs={"slug": "test-slug"}
        ))
        first_object = response.context.get("page").object_list[0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_author_0 = first_object.author.username
        self.assertEqual(post_text_0, "Пост")
        self.assertEqual(post_group_0, self.test_group.title)
        self.assertEqual(post_author_0, self.test_author.username)
        self.assertTrue(
            re.fullmatch(r"posts/test_image.*\.gif", "posts/test_image.gif")
        )

    def test_edit_page_show_correct_context(self):
        response = self.author_client.get(reverse(
            "posts:post_edit",
            kwargs={"username": self.test_author.username, "post_id": 1}
        ))
        form_fields = {
            "text": forms.fields.CharField,
            "image": forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_page_show_correct_context(self):
        response = self.guest_client.get(reverse(
            "posts:profile",
            kwargs={"username": self.test_author.username}
        ))
        first_object = response.context.get("page").object_list[0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_author_0 = first_object.author.username
        self.assertEqual(post_text_0, "Пост")
        self.assertEqual(post_group_0, self.test_group.title)
        self.assertEqual(post_author_0, self.test_author.username)
        self.assertTrue(
            re.fullmatch(r"posts/test_image.*\.gif", "posts/test_image.gif")
        )

    def test_post_view_page_show_correct_context(self):
        response = self.guest_client.get(reverse(
            "posts:post",
            kwargs={"username": self.test_author.username, "post_id": 1}
        ))
        first_object = response.context.get("post")
        post_text = first_object.text
        post_group = first_object.group.title
        post_author = first_object.author.username
        self.assertEqual(post_text, "Пост 1")
        self.assertEqual(post_group, self.test_group.title)
        self.assertEqual(post_author, self.test_author.username)
        self.assertTrue(
            re.fullmatch(r"posts/test_image.*\.gif", "posts/test_image.gif")
        )

    def test_paginator_show_correct_amount(self):
        response = self.guest_client.get(reverse("posts:index"), {"page": 1})
        pages = response.context["page"]
        self.assertEqual(len(pages), 10)

    def test_new_post_page_show_correct_context(self):
        response = self.authorized_client.get(reverse("posts:new_post"))
        form_fields = {
            "text": forms.fields.CharField,
            "image": forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_wrong_url_returns_404(self):
        response = self.guest_client.get("/404/")
        self.assertEqual(response.status_code, 404)
