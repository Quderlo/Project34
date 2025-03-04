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
        help_text='IP адрес камеры внутри сети',
    )

    port = models.PositiveIntegerField(
        verbose_name='Порт',
        help_text='Порт у камеры',
    )

    rtsp_path = models.CharField(
        max_length=255,
        verbose_name='Путь RTSP',
        help_text="Путь RTSP потока. Например, '/live/av0' или 'Streaming/Channels/101'."
    )

    username = models.CharField(
        max_length=255,
        verbose_name='Имя пользователя',
        help_text='Имя которое указывается при аутентификации к камере',
    )

    password = models.CharField(
        max_length=255,
        verbose_name='Пароль',
        help_text='Пароль который указывается при аутентификации к камере',
    )

    rtsp_link = models.URLField(
        verbose_name='RTSP - ссылка',
        blank=True,
        help_text='Если ссылка не указана, будет автоматически сгенерирована.',
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

    def generate_rtsp_link(self) -> str:
        """
        Генерирует RTSP-ссылку с использованием данных авторизации и пути RTSP.
        """
        if self.rtsp_link:
            return self.rtsp_link

        auth_part = f"{self.username}:{self.password}@"
        return f"rtsp://{auth_part}{self.ip_address}:{self.port}{self.rtsp_path}"


    def _check_connection(self):
        # TODO: Сделать проверку rtsp
        try:
            link = str(self.ip_address) + ":" + str(self.port)
            response = requests.get(link, timeout=3)
            return response.status_code == 200

        except Exception:
            return False
        pass

    def save(self, *args, **kwargs):
        if not self.rtsp_link:
            self.rtsp_link = self.generate_rtsp_link()
        super().save(*args, **kwargs)


    class Meta:
        verbose_name='Камера'
        verbose_name_plural='Камеры'