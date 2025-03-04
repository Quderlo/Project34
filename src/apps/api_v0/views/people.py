from rest_framework import viewsets, permissions

from apps.api_v0.serializers.people import PeopleModelSerializer
from apps.models.models import Person


class PeopleModelViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'head', 'options', 'post', 'put', 'patch', 'delete']
    serializer_class = PeopleModelSerializer
    queryset = Person.objects.all()
    permission_classes = [permissions.IsAuthenticated]