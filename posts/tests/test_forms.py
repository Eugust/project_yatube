import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.forms import PostForm
from posts.models import Follow, Post, Group

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.author = User.objects.create_user(username="Автор")
        cls.group = Group.objects.create(slug="first")
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        Post.objects.create(
            text="Пост",
            group=cls.group,
            author=cls.author,
            image=cls.uploaded
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
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
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            "text": "Пост",
            "image": uploaded,
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
                author=self.author,
                text="Пост",
                image="posts/small.gif"
            ).exists()
        )

    def test_edit_post(self):
        posts_count = Post.objects.count()
        new_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='new.gif',
            content=new_gif,
            content_type='image/gif'
        )
        form_data = {
            "text": "Новый пост",
            "image": uploaded,
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
                author=self.author,
                image="posts/new.gif"
            ).exists()
        )

    def test_authorized_can_comment(self):
        form_data = {
            "text": "test comment"
        }
        response = self.authorized_client.post(
            reverse(
                "posts:add_comment",
                kwargs={"username": self.author.username, "post_id": 1}
            ),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            "posts:post",
            kwargs={"username": self.author.username, "post_id": 1}
        ))

    def test_anon_cant_comment(self):
        form_data = {
            "text": "test comment"
        }
        response = self.guest_client.post(
            reverse(
                "posts:add_comment",
                kwargs={"username": self.author.username, "post_id": 1}
            ),
            data=form_data,
            follow=True,
        )
        add = "%25D0%2590%25D0%25B2%25D1%2582%25D0%25BE%25D1%2580"
        self.assertRedirects(
            response,
            f"/auth/login/?next=/{add}/1/comment"
        )

    def test_authorized_can_sub(self):
        sub_count = Follow.objects.count()
        follower = User.objects.create(username="follower")
        form_data = {
            "user": follower,
            "author": self.author
        }
        response = self.authorized_client.post(
            reverse(
                "posts:profile_follow",
                kwargs={"username": self.author.username}
            ),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            "posts:profile",
            kwargs={"username": self.author.username}
        ))
        self.assertEqual(Follow.objects.count(), sub_count + 1)

    def test_authorized_can_sub(self):
        follower = User.objects.create(username="follower")
        form_data = {
            "user": follower,
            "author": self.author
        }
        self.authorized_client.post(
            reverse(
                "posts:profile_follow",
                kwargs={"username": self.author.username}
            ),
            data=form_data,
            follow=True,
        )
        sub_count = Follow.objects.count()
        del_form_data = {
            "user": follower,
            "author": self.author
        }
        del_response = self.authorized_client.post(
            reverse(
                "posts:profile_unfollow",
                kwargs={"username": self.author.username}
            ),
            data=del_form_data,
            follow=True,
        )
        self.assertRedirects(del_response, reverse(
            "posts:profile",
            kwargs={"username": self.author.username}
        ))
        self.assertEqual(Follow.objects.count(), sub_count - 1)

    def test_group_label(self):
        group_label = PostCreateFormTests.form.fields["group"].label
        self.assertEqual(group_label, "Группа")

    def test_text_label(self):
        text_label = PostCreateFormTests.form.fields["text"].label
        self.assertEqual(text_label, "Пост")
