from rest_framework import serializers

from apps.models.models import Camera


class CameraModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = ('id', 'name', 'ip_address', 'port', 'image_path', 'image_link',
                  'electronic_lock', 'is_live')

        read_only_fields = ('is_live', )
