from rest_framework import viewsets, permissions

from apps.api_v0.serializers.lock import ElectronicLockModelSerializer
from apps.models.models import ElectronicLock


class ElectronicLockModelViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'head', 'options', 'post', 'put', 'patch', 'delete']
    queryset = ElectronicLock.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ElectronicLockModelSerializer