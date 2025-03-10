import dlib
import cv2
import numpy as np
import base64
from rest_framework import serializers
from django.core.validators import RegexValidator
from apps.models.models import Person


class PeopleModelSerializer(serializers.ModelSerializer):
    photo_base64 = serializers.CharField(
        write_only=True,
        required=False,
        help_text="Фотография в base64",
    )

    photo_file = serializers.FileField(
        write_only=True,
        required=False,
        help_text="Фотография"
    )

    class Meta:
        model = Person
        fields = ('first_name', 'last_name', 'patronymic',
                  'is_active', 'groups', 'photo_base64', 'photo_file')
        read_only_fields = ('created_at', 'last_seen', 'face_data')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Инициализация моделей dlib
        self.detector = dlib.get_frontal_face_detector()
        self.shape_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        self.face_recognizer = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")

    name_validator = RegexValidator(
        regex=r'^[а-яА-ЯёЁa-zA-Z\- ]+$',
        message='Допустимы только буквы, дефисы и пробелы'
    )

    def validate(self, attrs):
        if not attrs.get('photo_file') and not attrs.get('photo_base64'):
            raise serializers.ValidationError("Необходимо указать photo_file или photo_base64")
        if attrs.get('photo_file') and attrs.get('photo_base64'):
            raise serializers.ValidationError("Используйте только один источник фотографии")
        return attrs

    def _process_photo(self, validated_data):
        if 'photo_file' in validated_data:
            photo_file = validated_data.pop('photo_file')
            return photo_file.read()
        if 'photo_base64' in validated_data:
            header, data = validated_data.pop('photo_base64').split(';base64,')
            return base64.b64decode(data)
        return None

    def _get_face_descriptor(self, image_bytes):
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise serializers.ValidationError("Неверный формат изображения")

            rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            faces = self.detector(rgb_image)

            if len(faces) != 1:
                raise serializers.ValidationError("На фото должно быть ровно одно лицо")

            shape = self.shape_predictor(rgb_image, faces[0])
            descriptor = self.face_recognizer.compute_face_descriptor(rgb_image, shape)

            return np.array(descriptor, dtype=np.float32).tobytes()

        except Exception as e:
            raise serializers.ValidationError(f"Ошибка обработки лица: {str(e)}")

    def validate_first_name(self, value):
        self.name_validator(value)
        return value.strip().title()

    def validate_last_name(self, value):
        self.name_validator(value)
        return value.strip().title()

    def validate_patronymic(self, value):
        if value:
            self.name_validator(value)
            return value.strip().title()
        return value

    def create(self, validated_data):
        image_bytes = self._process_photo(validated_data)
        face_data = self._get_face_descriptor(image_bytes)
        validated_data['face_data'] = face_data
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'photo_file' in validated_data or 'photo_base64' in validated_data:
            image_bytes = self._process_photo(validated_data)
            face_data = self._get_face_descriptor(image_bytes)
            validated_data['face_data'] = face_data
        return super().update(instance, validated_data)