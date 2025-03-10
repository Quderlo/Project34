from django.db import models

from apps.models.models.camera import Camera
from apps.models.models.people import Person


class AccessTime(models.Model):

    people = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        verbose_name='Человек',
        help_text='Человек которого заметила камера',
    )

    camera = models.ForeignKey(
        Camera,
        on_delete=models.PROTECT,
        verbose_name='Камера',
        help_text='Камера с которой был замечен человек',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    def __str__(self):
        return f'{self.people} {self.created_at} {self.camera}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionError("Удаление записей запрещено")

    class Meta:
        verbose_name='Доступ'
        verbose_name_plural='Доступы'
        permissions = [
            ('view_only_access', 'Can view access records'),
        ]