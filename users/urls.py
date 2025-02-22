from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import RegisterView,LogoutView,CurrentUserView,CustomTokenObtainPairView,UserListAPIView,RetrieveUpdateDestroyUserAPIView


urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('token/',CustomTokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('token/refresh/',CustomTokenObtainPairView.as_view(),name='token_refresh'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('me/',CurrentUserView.as_view(),name='current_user'),
    path('',UserListAPIView.as_view(),name="users_list"),
    path('<int:pk>',RetrieveUpdateDestroyUserAPIView.as_view(),name="single_user")
]
   
