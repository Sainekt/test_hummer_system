from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinLengthValidator
from django.db import models

from .constants import MAX_150, MAX_254


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    email = models.EmailField(
        verbose_name='Адрес электронной почты.',
        error_messages={
            'unique': 'Адрес электронной почты уже используется.'
        },
        max_length=MAX_254,
        blank=True,
        null=True,
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=MAX_150,
        unique=True,
        error_messages={
            'unique': 'Пользователь с таким именем уже существует.'
        },
        blank=True,
        null=True,

    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_150,
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_150,
        blank=True,
        null=True,
    )
    # В интернете написано что от 4-18 длинна номеров.
    phone_number = models.CharField(
        verbose_name='Телефонный номер',
        unique=True,
        max_length=18,
        validators=[MinLengthValidator(4)]
    )
    region = models.CharField(
        verbose_name='Регион',
        max_length=10,
        null=True,
        blank=True,
    )
    referal_code = models.CharField(
        verbose_name='Реферальный код пользователя.',
        max_length=6,
        unique=True,
    )
    invite_code = models.CharField(
        verbose_name='Код приглашения',
        max_length=6,
        blank=True,
        null=True,
    )

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return (self.username if self.username else self.phone_number)


class UserConfirmCode(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        )
    confir_code = models.CharField(
        verbose_name='Код активации',
        max_length=4,
        )
    created_at = models.DateTimeField(
        verbose_name='Дата и время создания',
        auto_now_add=True
        )
    update_at = models.DateTimeField(
        verbose_name='Дата и время обновления',
        auto_now=True
    )

    def __str__(self):
        return f'{self.user.username} - {self.activation_code}'
