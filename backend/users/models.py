from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    subscribers = models.ManyToManyField(
        to='self',
        through='Subscription',
        symmetrical=False,
        related_name='subscription_users',
        verbose_name='Подписки'
    )
    first_name = models.CharField(_('first name'), max_length=150, blank=False)
    last_name = models.CharField(_('last name'), max_length=150, blank=False)
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.first_name


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор',
    )
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

        constraints = [
            models.UniqueConstraint(
                fields=['author', 'subscriber'],
                name='unique_user_subscriber'
            ),
            models.CheckConstraint(
                check=models.Q(author=models.F('subscriber')),
                name='check_equal_author_subscriber'
            )
        ]

    def __str__(self):
        return f'{self.subscriber} подписан на {self.author}'
