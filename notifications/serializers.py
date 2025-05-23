from rest_framework import serializers
from .models import Notifications

class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model=Notifications
        fields="__all__"
        read_only_fields = ["id", "created_at", "user"] 