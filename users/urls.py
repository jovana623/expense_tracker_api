from django.urls import path
from .views import RegisterView,LogoutView,CurrentUserView
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('current_user/',CurrentUserView.as_view(),name='current_user'),
    path('token/',TokenObtainPairView.as_view(),name='token'),
    path('token/refresh/',TokenRefreshView.as_view(),name='token_refresh')
]
