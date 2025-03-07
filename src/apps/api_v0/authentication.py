from rest_framework.authentication import SessionAuthentication

class SessionAuthNoCSRF(SessionAuthentication):
    def enforce_csrf(self, request):
        # Отключаем проверку CSRF для аутентификации по сессиям
        return