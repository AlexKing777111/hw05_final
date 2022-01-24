from multiprocessing import AuthenticationError
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Название",
    )
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(
        verbose_name="Описание",
    )

    class Meta:
        verbose_name = "Сообщество"
        verbose_name_plural = "Сообщества"

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name="Текст поста", help_text="Текст нового поста"
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата публикации"
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Группа",
        help_text="Группа, к которой будет относиться пост",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
    )
    image = models.ImageField("Картинка", upload_to="posts/", blank=True)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Пост"
        verbose_name_plural = "Посты"


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Комментарий",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор комментария",
    )
    text = models.TextField(
        verbose_name="Комментарий", help_text="Введите текст комментария"
    )
    created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата публикации"
    )

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
