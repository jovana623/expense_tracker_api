from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Notifications
from .serializers import NotificationSerializer


class NotificationsListAPIView(generics.ListAPIView):
    serializer_class=NotificationSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        return Notifications.objects.filter(user=self.request.user)
    

class RetrieveUpdateDestoryNotificationAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Notifications.objects.all()
    serializer_class=NotificationSerializer
    permission_classes=[IsAuthenticated]