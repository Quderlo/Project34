from rest_framework import serializers

from apps.models.models import Camera


class CameraModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = ('id', 'name', 'ip_address', 'port', 'rtsp_path',
                  'username', 'password', 'electronic_lock',
                  'rtsp_link', 'is_live')

        read_only_fields = ('rtsp_link', 'is_live')
