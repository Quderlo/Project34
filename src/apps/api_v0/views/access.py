from rest_framework import viewsets, permissions

from apps.api_v0.serializers.access import AccessModelSerializer
from apps.models.models import AccessTime


class AccessModelViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'head', 'options', 'post']
    permission_classes = [permissions.IsAuthenticated]
    queryset = AccessTime.objects.all()
    serializer_class = AccessModelSerializer

    def get_queryset(self):
        return super().get_queryset().select_related('people', 'camera')

