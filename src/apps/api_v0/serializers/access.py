import base64
import binascii

import numpy as np
from rest_framework import serializers

from apps.api_v0.authentication import SessionAuthNoCSRF
from apps.models.models import AccessTime, Camera, Person


class AccessModelSerializer(serializers.ModelSerializer):
    face_data = serializers.CharField(write_only=True)
    camera_id = serializers.IntegerField(write_only=True)
    authentication_classes = [SessionAuthNoCSRF]

    class Meta:
        model = AccessTime
        fields = ('face_data', 'camera_id')
        read_only_fields = ('camera', 'people', 'created_at')

    def validate_face_data(self, value):
        """Декодирование base64 и преобразование в вектор"""
        try:
            # Удаление префикса данных при наличии
            if ';base64,' in value:
                header, data = value.split(';base64,', 1)
            else:
                data = value

            decoded_data = base64.b64decode(data)
            return decoded_data
        except (TypeError, binascii.Error, ValueError) as e:
            raise serializers.ValidationError(f"Некорректный формат данных: {str(e)}")

    def validate(self, attrs):
        face_data = attrs['face_data']
        camera_id = attrs['camera_id']

        try:
            camera = Camera.objects.get(id=camera_id)
        except Camera.DoesNotExist:
            raise serializers.ValidationError({"camera_id": "Камера не найдена"})

        try:
            # Преобразование бинарных данных в numpy array
            input_vector = np.frombuffer(face_data, dtype=np.float32)

            if input_vector.shape != (128,):
                raise serializers.ValidationError({
                    "face_data": "Неверная размерность вектора (ожидается 128 элементов)"
                })

        except Exception as e:
            raise serializers.ValidationError({"face_data": str(e)})

        # Остальная логика сравнения остается без изменений
        input_norm = np.linalg.norm(input_vector)
        persons = Person.objects.all()

        best_match = None
        min_distance = 1.0
        threshold = 0.6

        for person in persons:
            try:
                db_vector = np.frombuffer(person.face_data.tobytes(), dtype=np.float32)
                distance = np.linalg.norm(np.array(db_vector) - input_norm)

                if distance < min_distance and distance < (1 - threshold):
                    min_distance = distance
                    best_match = person
            except Exception as e:
                print(f"Error processing person {person.id}: {str(e)}")
                continue

        if not best_match:
            raise serializers.ValidationError({
                "detail": "Лицо не распознано",
                "similarity": float(1 - min_distance),
                "camera": camera.name
            })

        attrs['person'] = best_match
        attrs['camera'] = camera
        return attrs

    # Остальные методы остаются без изменений

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