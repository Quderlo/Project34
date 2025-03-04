from rest_framework import viewsets, permissions

from apps.api_v0.serializers.camera import CameraModelSerializer
from apps.models.models import Camera


class CameraModelViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'head', 'options', 'post', 'put', 'patch', 'delete']
    queryset = Camera.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CameraModelSerializer