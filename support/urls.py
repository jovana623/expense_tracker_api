from django.urls import path
from .views import SupportThreadCreateAPIView,SupportThreadRetrieveUpdateDestroyAPIView,SupportMessageListCreateAPIView,MyThreadsAPIView,OpenThreadsAPIView,ClosedThreadsAPIView,ChangeThreadStatusAPIView,SupportThreadSearchAPIView

urlpatterns=[
    path('threads/create/',SupportThreadCreateAPIView.as_view(),name='create-thread'),
    path('threads/my/',MyThreadsAPIView.as_view(),name="my-threads"),
    path('threads/open/',OpenThreadsAPIView.as_view(),name="open-threads"),
    path('threads/closed/',ClosedThreadsAPIView.as_view(),name="closed-threads"),
    path('threads/<int:pk>/',SupportThreadRetrieveUpdateDestroyAPIView.as_view(),name='single-thread'),
    path('threads/<int:pk>/change-status/',ChangeThreadStatusAPIView.as_view(),name="change-status"),
    path('threads/search/',SupportThreadSearchAPIView.as_view(),name='search-thread'),
    path('threads/<int:thread_id>/messages/',SupportMessageListCreateAPIView.as_view(),name='thread-messages')
]