from django.urls import path
from . import views


urlpatterns = [
    path('create_saving',views.CreateSavingAPIView.as_view(),name='create_saving'),
    path("",views.ListSavingsAPIView.as_view(),name='savings'),
    path("<int:pk>",views.RetrieveUpdateDestroySavingAPIView.as_view(),name='single_saving'),
    path('create_payment',views.CreatePaymentAPIView.as_view(),name='create_payment'),
    path('payments/',views.ListPaymentAPIView.as_view(),name='payments'),
    path('payments/<int:pk>',views.RetrieveUpdateDestroyPaymentAPIView.as_view(),name='single_payment')
]
