import requests
from django.db import models

from apps.models.models.elock import ElectronicLock


class Camera(models.Model):
    name = models.CharField(
        verbose_name='Название камеры',
        help_text='Например местоположение камеры',
        max_length=100,
    )

    ip_address = models.GenericIPAddressField(
        verbose_name="IP адрес",
        help_text='IP адрес сервиса внутри сети',
    )

    port = models.PositiveIntegerField(
        verbose_name='Порт',
        blank=True,
        null=True,
        help_text='Порт у сервиса если имеется',
    )

    image_path = models.CharField(
        max_length=50,
        verbose_name = 'Путь к изображению',
        help_text = 'Путь на сервисе к изображению например /image/0',
    )

    image_link = models.URLField(
        max_length=100,
        verbose_name='Ссылка на изображение',
        help_text='Ссылка на сервис отдающий кадры',
        blank=True,
    )

    is_live = models.BooleanField(
        verbose_name='Активна',
        help_text='Статус работы камеры',
        default=False,
    )

    electronic_lock = models.ForeignKey(
        ElectronicLock,
        verbose_name='Замок',
        help_text='Внешний ключ на замок который открывает камера',
        # TODO: Заменить на PROTECT при релизе
        on_delete=models.CASCADE,
    )


    def __str__(self):
        return f"{self.name} ({self.ip_address})"

    def _check_connection(self):
        try:
            link = str(self.ip_address) + ":" + str(self.port)
            response = requests.get(link, timeout=3)
            return response.status_code == 200

        except Exception:
            return False
        pass

    def save(self, *args, **kwargs):
        link = self.ip_address
        if self.port:
            link += ":" + str(self.port)

        self.image_link = 'http://' + link + self.image_path

        super().save(*args, **kwargs)


    class Meta:
        verbose_name='Камера'
        verbose_name_plural='Камеры'