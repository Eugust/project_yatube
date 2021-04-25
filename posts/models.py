from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name="Название группы",
        max_length=200,
        help_text="Введите название группы"
    )
    slug = models.SlugField(
        verbose_name="Слаг",
        max_length=100,
        unique=True,
        help_text="Укажите адрес для страницы группы"
    )
    description = models.TextField(
        verbose_name="Описание группы",
        help_text="Добавьте описание группы"
    )

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name="Пост",
        help_text="Напишите свой пост"
    )
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts")
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="group_posts")
    image = models.ImageField(
        verbose_name="Картинка",
        upload_to="posts/",
        blank=True,
        null=True,
        help_text="Загрузите картинку"
    )

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self) -> str:
        return self.text[:15]


class Comment(models.Model):
    text = models.TextField(
        verbose_name="Комментарий",
        help_text="Добавьте к посту свой комментарий",
    )
    created = models.DateTimeField(
        verbose_name="Время создания",
        auto_now_add=True,
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    class Meta:
        ordering = ["created"]

    def __str__(self):
        return "Комментарий от {} для поста {}".format(self.author, self.post)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
    )

    def __str__(self):
        return "{} подписался на {} ".format(self.user, self.author)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_subs"
            )
        ]
