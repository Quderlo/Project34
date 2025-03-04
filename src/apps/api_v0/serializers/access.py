from rest_framework import serializers
import base64
import binascii

from apps.models.models import AccessTime, Camera, Person


class AccessModelSerializer(serializers.ModelSerializer):
    face_data = serializers.CharField(write_only=True)
    camera_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = AccessTime
        fields = ('face_data', 'camera_id')
        read_only_fields = ('camera', 'people', 'created_at')

    def validate_face_data(self, value):
        """Валидация и преобразование base64 в бинарные данные"""
        try:
            return base64.b64decode(value)
        except (TypeError, binascii.Error):
            raise serializers.ValidationError("Некорректный формат base64")

    def validate(self, attrs):
        """Основная логика валидации"""
        # Получаем уже декодированные бинарные данные
        face_data = attrs['face_data']
        camera_id = attrs['camera_id']

        # Поиск камеры
        try:
            camera = Camera.objects.get(id=camera_id)
        except Camera.DoesNotExist:
            raise serializers.ValidationError({"camera_id": "Камера не найдена"})

        # Поиск человека по биометрическим данным (заглушка)
        person = Person.objects.filter(face_data=face_data).first()

        if not person:
            raise serializers.ValidationError({"face_data": "Человек не распознан"})

        attrs['person'] = person
        attrs['camera'] = camera
        return attrs

    def create(self, validated_data):
        person = validated_data['person']
        camera = validated_data['camera']

        # Обновляем время последнего обнаружения
        person.is_seen_by_camera(camera)

        # Создаем запись о доступе
        return AccessTime.objects.create(
            people=person,
            camera=camera
        )