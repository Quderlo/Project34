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

    name_validator = RegexValidator(
        regex=r'^[а-яА-ЯёЁa-zA-Z\- ]+$',
        message='Допустимы только буквы, дефисы и пробелы'
    )

    def validate(self, attrs):
        # Проверка наличия хотя бы одного источника фото
        if not attrs.get('photo_file') and not attrs.get('photo_base64'):
            raise serializers.ValidationError(
                "Необходимо указать photo_file или photo_base64"
            )

        # Запрет на одновременную отправку обоих полей
        if attrs.get('photo_file') and attrs.get('photo_base64'):
            raise serializers.ValidationError(
                "Используйте только один источник фотографии"
            )

        return attrs

    def _process_photo(self, validated_data):
        """Обработка фото из разных источников"""
        # Обработка файла
        if 'photo_file' in validated_data:
            photo_file = validated_data.pop('photo_file')
            return photo_file.read()

        # Обработка base64
        if 'photo_base64' in validated_data:
            header, data = validated_data.pop('photo_base64').split(';base64,')
            return base64.b64decode(data)

        return None

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
        # Обработка фото поиск лица
        photo = validated_data.pop('photo', None)
        # TODO: Прикрутить нейронку

        # Заглушка для обработки
        validated_data['face_data'] = b'work'

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Обработка фото поиск лица

        # TODO: Прикрутить нейронку
        if 'photo' in validated_data:
            photo = validated_data.pop('photo')
            validated_data['face_data'] = b'work_updated'

        return super().update(instance, validated_data)