from django.contrib.auth import login, get_user_model
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from apps.api_v0.serializers.login import LoginSerializer

User = get_user_model()

class LoginViewSet(viewsets.ViewSet):
    http_method_names = ['post']
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response({'detail': 'Вы уже авторизованы'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            login(request, user)

            return Response({'detail': 'Успешный вход'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
