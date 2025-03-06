from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if not username:
            raise ValidationError({"username": "Пожалуйста, укажите имя пользователя."})
        if not password:
            raise ValidationError({"password": "Пожалуйста, укажите пароль."})

        user = authenticate(username=username, password=password)
        if not user:
            raise ValidationError({"username": "Неверное имя пользователя или пароль."})

        data["user"] = user
        return data
