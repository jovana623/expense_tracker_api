from django.urls import re_path
from .consumers import ChatConsumer,MessageNotificationConsumer

websocket_urlpatterns=[
    re_path(r'ws/support/chat/(?P<thread_id>\d+)/$',ChatConsumer.as_asgi()),
    re_path(r'ws/support/message-notifications/$',MessageNotificationConsumer.as_asgi())
] 