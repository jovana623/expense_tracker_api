from django.urls import path
from .views import NotificationsListAPIView,RetrieveUpdateDestoryNotificationAPIView

urlpatterns=[
    path("",NotificationsListAPIView.as_view(),name="notifications"),
    path('<int:pk>',RetrieveUpdateDestoryNotificationAPIView.as_view(),name="notification")
]