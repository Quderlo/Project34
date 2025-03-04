from django.contrib.auth.models import Group
from django.db import models
from django.utils import timezone

from apps.models.models.camera import Camera


class Person(models.Model):
    first_name = models.CharField(
        max_length=50,
        verbose_name='Имя'
    )

    last_name = models.CharField(
        max_length=50,
        verbose_name='Фамилия'
    )

    patronymic = models.CharField(
        max_length=50,
        verbose_name='Отчество',
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
        blank=True,
    )

    last_seen = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата последнего появления',
        help_text='Когда последний раз камера замечала этого человека',
        blank=True,
    )

    is_active = models.BooleanField(
        verbose_name='Активен',
        default=True,
        help_text='Пропускать пользователя или нет'
    )

    face_data = models.BinaryField(
        verbose_name='Лицевые данные',
        help_text='Вектор лицевых данных в бинарном виде',
        blank=True,
        null=True,
    )

    # Привязка сотрудника к группам Django
    groups = models.ManyToManyField(
        Group,
        verbose_name="Группы сотрудника",
        blank=True,
        help_text="Группы доступа, к которым относится сотрудник"
    )

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


    def is_seen_by_camera(self) -> None:
        self.last_seen = timezone.now()
        self.save()

    class Meta:
        verbose_name='Человек'
        verbose_name_plural='Люди'


