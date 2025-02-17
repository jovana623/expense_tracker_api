from django.urls import path
from .views import RegisterView,LogoutView,CurrentUserView,CustomTokenObtainPairView


urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('token/',CustomTokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('token/refresh/',CustomTokenObtainPairView.as_view(),name='token_refresh'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('me/',CurrentUserView.as_view(),name='current_user'),
]
   