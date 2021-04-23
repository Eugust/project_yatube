from django.test import TestCase
from django.contrib.auth import get_user_model

from posts.models import Group, Post

User = get_user_model()


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.group = Group.objects.create(
            title="Название"
        )

    def test_title_label(self):
        group = GroupModelTest.group
        verbose = group._meta.get_field('title').verbose_name
        self.assertEqual(verbose, "Название группы")

    def test_title_help_text(self):
        group = GroupModelTest.group
        help_text = group._meta.get_field('title').help_text
        self.assertEqual(help_text, "Введите название группы")

    def test_object_name_is_title_field(self):
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.post = Post.objects.create(
            text="Описание поста",
            author=User.objects.create()
        )

    def test_title_label(self):
        post = PostModelTest.post
        verbose = post._meta.get_field('text').verbose_name
        self.assertEqual(verbose, "Пост")

    def test_title_help_text(self):
        post = PostModelTest.post
        help_text = post._meta.get_field('text').help_text
        self.assertEqual(help_text, "Напишите свой пост")

    def test_len_title_field_object_name(self):
        post = PostModelTest.post
        expected_len = 15
        self.assertTrue(expected_len > len(post.text))
