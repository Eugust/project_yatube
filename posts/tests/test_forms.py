import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.forms import PostForm
from posts.models import Post, Group

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.author = User.objects.create_user(username="Автор")
        Group.objects.create(
            slug="first",
        )
        Post.objects.create(
            text="Пост",
            group=Group.objects.get(slug="first"),
            author=cls.author,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        # авторизованный клиент
        self.user = User.objects.create_user(username="Andrey")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # автор
        self.author = User.objects.get(username="Автор")
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_create_post(self):
        posts_count = Post.objects.count()
        image = SimpleUploadedFile(
            name='small.gif',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00',
            content_type='image/gif'
        )
        form_data = {
            "text": "Пост",
            "image": image,
        }
        response = self.authorized_client.post(
            reverse("posts:new_post"),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse("posts:index"))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=User.objects.get(username="Автор"),
                text="Пост",
                image="posts/small.gif"
            ).exists()
        )

    def test_edit_post(self):
        posts_count = Post.objects.count()
        image = SimpleUploadedFile(
            name='small.gif',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00',
            content_type='image/gif'
        )
        form_data = {
            "text": "Новый пост",
            "image": image,
        }
        response = self.author_client.post(
            reverse(
                "posts:post_edit",
                kwargs={"username": self.author.username, "post_id": 1}
            ),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            "posts:post",
            kwargs={"username": self.author.username, "post_id": 1}
        ))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text="Новый пост",
                author=User.objects.get(username="Автор"),
                image="posts/small.gif"
            ).exists()
        )

    def test_group_label(self):
        group_label = PostCreateFormTests.form.fields["group"].label
        self.assertEqual(group_label, "Группа")

    def test_text_label(self):
        text_label = PostCreateFormTests.form.fields["text"].label
        self.assertEqual(text_label, "Пост")
