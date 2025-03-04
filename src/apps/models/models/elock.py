from django.db import models
import requests

class ElectronicLock(models.Model):
    ip_address = models.GenericIPAddressField(
        verbose_name='IP адрес',
        help_text='Адрес API контроллера замка',
    )

    status_link = models.URLField(
        verbose_name='URL статуса',
        help_text='Эндпоинт статуса реле',
    )

    lock_link = models.URLField(
        verbose_name='URL закрытия',
        help_text='Эндпоинт закрытия реле',
    )

    unlock_link = models.URLField(
        verbose_name='URL открытия',
        help_text='Эндпоинт открытия реле',
    )

    is_online = models.BooleanField(
        verbose_name='Соединение',
        default=False,
        editable=False,
    )

    def __str__(self):
        return f"Замок {self.ip_address}"

    def save(self, *args, **kwargs):
        self.is_online = self._check_connection()
        super().save(*args, **kwargs)

    def _check_connection(self):

        # TODO: Сделать проверку rtsp

        try:
            response = requests.get(self.status_link, timeout=3)
            return response.status_code == 200

        except Exception:
            return False

    class Meta:
        verbose_name='Замок'
        verbose_name_plural='Замки'