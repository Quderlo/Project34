import json
import logging
from typing import Tuple, Optional, Dict, Any
from urllib.parse import urljoin

from django.contrib.auth import get_user_model
from django.db import models
import requests
from requests import RequestException

User = get_user_model()
logger = logging.getLogger(__name__)

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

    secret_key = models.CharField(
        max_length=255,
        verbose_name='Секретный ключ',
        help_text='Секретный ключ к API замка',
    )

    def __str__(self):
        return f"Замок {self.ip_address}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Status:
        OPEN = 'open'
        CLOSED = 'closed'
        UNKNOWN = 'unknown'

    class ErrorMessages:
        INVALID_JSON = "Некорректный JSON в ответе"
        TIMEOUT = "Таймаут подключения"
        REQUEST_ERROR = "Ошибка запроса: {error}"
        INVALID_STATUS = "Некорректный статус в ответе"
        ACTION_FAILED = "Действие не подтверждено"

    def _make_request(self, url: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Улучшенный метод запроса с подписью"""
        try:
            headers = {
                "X-Lock-Signature": self.secret_key,
                "User-Agent": "SmartLockSystem/1.0"
            }

            full_url = urljoin(f"http://{self.ip_address}/", url)

            response = requests.get(
                full_url,
                headers=headers,
                timeout=5
            )
            response.raise_for_status()

            return True, "Успешный запрос", response.json()

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from lock {self.ip_address}")
            return False, self.ErrorMessages.INVALID_JSON, None
        except requests.Timeout:
            logger.warning(f"Timeout connecting to lock {self.ip_address}")
            return False, self.ErrorMessages.TIMEOUT, None
        except RequestException as e:
            logger.error(f"Lock communication error: {str(e)}")
            return False, self.ErrorMessages.REQUEST_ERROR.format(error=str(e)), None

    def update_connection_status(self, success: bool):
        """Обновление статуса подключения"""
        self.is_online = success
        self.save(update_fields=['is_online'])

    def check_status(self) -> Tuple[bool, str]:
        """Проверка статуса подключения с логированием"""
        success, message, data = self._make_request(self.status_link)
        self.update_connection_status(success)
        return success, message

    def check_active(self) -> Tuple[bool, str]:
        """Определение состояния замка с валидацией ответа"""
        success, message, data = self._make_request(self.status_link)

        if not success:
            return False, message

        if not data or 'status' not in data:
            return False, self.ErrorMessages.INVALID_STATUS

        state = data['status'].lower()
        if state == self.Status.OPEN:
            return True, self.Status.OPEN
        elif state == self.Status.CLOSED:
            return True, self.Status.CLOSED

        return False, self.ErrorMessages.INVALID_STATUS

    def _perform_lock_action(self, url: str, action: str, user: User) -> Tuple[bool, str]:
        """Общий метод для выполнения действий с замком"""
        success, message, data = self._make_request(url)

        if not success:
            self.log_action(action + "_FAILED", user, success)
            return False, message

        if data and data.get('action') == 'success':
            self.log_action(action, user, True)
            return True, message

        self.log_action(action + "_ERROR", user, False)
        return False, self.ErrorMessages.ACTION_FAILED

    def open_lock(self, user: User) -> Tuple[bool, str]:
        return self._perform_lock_action(self.unlock_link, "OPEN", user)

    def close_lock(self, user: User) -> Tuple[bool, str]:
        return self._perform_lock_action(self.lock_link, "CLOSE", user)

    def log_action(self, action: str, user: User, status: bool):
        """Расширенное логирование действий"""
        LockLog.objects.create(
            lock=self,
            user=user,
            action=action,
            status=status,
            details=f"IP: {self.ip_address}"
        )

class LockLog(models.Model):
    lock = models.ForeignKey(ElectronicLock, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField()
    details = models.TextField(blank=True)