from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action

from apps.api_v0.serializers.lock import ElectronicLockModelSerializer
from apps.models.models import ElectronicLock

import logging

logger = logging.getLogger(__name__)


class ElectronicLockModelViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ElectronicLockModelSerializer
    queryset = ElectronicLock.objects.all()
    http_method_names = ['get', 'head', 'options', 'post', 'put', 'patch', 'delete']

    @action(detail=True, methods=['post'], name='open-lock')
    def open_lock(self, request, pk=None):
        """Открытие замка с полной проверкой ответа"""
        try:
            lock = self._get_lock_obj(request, pk)
            success, message = lock.open_lock(request.user)

            if success:
                logger.info(f"User {request.user} opened lock {pk}")
                return Response({'status': 'open', 'message': message}, status=status.HTTP_200_OK)

            logger.error(f"Open failed for lock {pk}: {message}")
            return Response({'error': 'Ошибка замка', 'message': message},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)

        except Exception as e:
            logger.exception(f"Open lock error: {str(e)}")
            return Response({'error': 'Ошибка сервера', 'message': 'Повторите запрос позже'
                        'или обратитесь в поддержку'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], name='close-lock')
    def close_lock(self, request, pk=None):
        """Закрытие замка с подтверждением состояния"""
        try:
            lock = self._get_lock_obj(request, pk)
            success, message = lock.close_lock(request.user)

            if success:
                logger.info(f"User {request.user} closed lock {pk}")
                return Response({'status': 'closed', 'message': message},
                                status=status.HTTP_200_OK)

            logger.error(f"Close failed for lock {pk}: {message}")
            return Response({'error': 'Ошибка замка', 'message': message},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)

        except Exception as e:
            logger.exception(f"Close lock error: {str(e)}")
            return Response({'error': 'Ошибка сервера', 'message': 'Повторите запрос позже'
                        'или обратитесь в поддержку'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'], name='check-status')
    def check_status(self, request, pk=None):
        """проверка статуса с состоянием замка"""
        try:
            lock = self._get_lock_obj(request, pk)
            connection_ok, _ = lock.check_status()
            state_ok, state_message = lock.check_active()

            response_data = {
                'online': connection_ok,
                'status': state_message,
            }

            status_code = status.HTTP_200_OK if connection_ok else status.HTTP_503_SERVICE_UNAVAILABLE
            return Response(response_data, status=status_code)

        except Exception as e:
            logger.error(f"Status check error: {str(e)}")
            return Response({'error': 'Ошибка сервера', 'message': 'Повторите запрос позже'
                        'или обратитесь в поддержку'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_lock_obj(self, request, pk=None) -> ElectronicLock:
        lock = get_object_or_404(ElectronicLock.objects, pk=pk)

        if not request.user.has_perm('locks.operate_lock', lock):
            logger.warning(f"Unauthorized access attempt by {request.user} to lock {pk}")
            raise PermissionDenied("You don't have permission to operate this lock")

        return lock