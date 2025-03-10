import numpy as np
from rest_framework import serializers

from apps.api_v0.authentication import SessionAuthNoCSRF
from apps.models.models import AccessTime, Camera, Person


class AccessModelSerializer(serializers.ModelSerializer):
    # Ожидаем, что клиент передаст список чисел (128 элементов)
    face_data = serializers.ListField(
        child=serializers.FloatField(), write_only=True
    )
    camera_id = serializers.IntegerField(write_only=True)
    authentication_classes = [SessionAuthNoCSRF]

    class Meta:
        model = AccessTime
        fields = ('face_data', 'camera_id')
        read_only_fields = ('camera', 'people', 'created_at')

    def _cosine_similarity(self, a, b):
        """Вычисление косинусной схожести"""
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        return dot_product / (norm_a * norm_b) if norm_a != 0 and norm_b != 0 else 0

    def validate(self, attrs):
        face_data = attrs['face_data']
        camera_id = attrs['camera_id']

        # Получение камеры
        try:
            camera = Camera.objects.get(id=camera_id)
        except Camera.DoesNotExist:
            raise serializers.ValidationError({"camera_id": "Камера не найдена"})
        print(face_data)
        # Преобразование списка в numpy array
        try:
            input_vector = np.array(face_data, dtype=np.float32)
            if input_vector.shape != (128,):
                raise ValueError("Неверная размерность входного вектора (ожидается 128 элементов)")
        except Exception as e:
            raise serializers.ValidationError({"face_data": str(e)})

        # Поиск кандидатов с заполненными face_data
        candidates = Person.objects.filter(face_data__isnull=False)

        best_match = None
        best_similarity = 0.0
        threshold = 0.5  # Оптимальный порог для dlib
        problematic_users = []

        for person in candidates:
            try:
                # Преобразование BinaryField в numpy array
                db_vector = np.frombuffer(person.face_data, dtype=np.float32)

                # Проверка размерности вектора из БД
                print(db_vector.shape)
                print(input_vector.shape)
                if db_vector.shape != (128,):
                    problematic_users.append(person.id)
                    continue

                similarity = self._cosine_similarity(input_vector, db_vector)

                if similarity > best_similarity and similarity > threshold:
                    best_similarity = similarity
                    best_match = person
                    print('similarity=', similarity)
                    print('best_similarity=', best_similarity)
                    print('best_match=', best_match)

            except Exception as e:
                print(f"Ошибка обработки пользователя {person.id}: {str(e)}")
                continue

        if problematic_users:
            print(f"Найдены пользователи с некорректным вектором: {problematic_users}")

        if not best_match:
            raise serializers.ValidationError({
                "detail": "Лицо не распознано",
                "similarity": best_similarity,
                "camera": camera.name
            })

        attrs['person'] = best_match
        attrs['camera'] = camera
        return attrs

    def create(self, validated_data):
        person = validated_data['person']
        camera = validated_data['camera']

        person.is_seen_by_camera()
        return AccessTime.objects.create(
            people=person,
            camera=camera
        )
