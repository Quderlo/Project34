from rest_framework import serializers

from apps.models.models import ElectronicLock


class ElectronicLockModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectronicLock
        fields = ('ip_address', 'status_link', 'lock_link',
                  'unlock_link', 'is_online', 'secret_key')

        read_only_fields = ('is_online',)
