from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    email = models.EmailField(
        verbose_name="Электронная почта",
        max_length=254,
        unique=True,
    )
    validator = RegexValidator(regex=r"^[\w.@+-]+\Z")
    username = models.CharField(
        verbose_name="Имя пользователя",
        max_length=150,
        null=False,
        blank=False,
        unique=True,
        validators=[validator],
    )
    first_name = models.CharField(verbose_name="Имя", max_length=150)
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=150,
    )
    avatar = models.ImageField(
        upload_to="users/images/",
        null=True,
        blank=True,
        verbose_name="Аватар",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
