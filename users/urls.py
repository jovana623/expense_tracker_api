from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import RegisterView,LogoutView,CurrentUserView,CustomTokenObtainPairView,UserListAPIView,RetrieveUpdateDestroyUserAPIView,ChangePasswordView,DeleteCurrentUserView,ResetAccountView,UpdateCurrencyView


urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('token/',CustomTokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('token/refresh/',CustomTokenObtainPairView.as_view(),name='token_refresh'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('me/',CurrentUserView.as_view(),name='current_user'),
    path('',UserListAPIView.as_view(),name="users_list"),
    path('<int:pk>',RetrieveUpdateDestroyUserAPIView.as_view(),name="single_user"),
    path('change_password/',ChangePasswordView.as_view(),name="change_password"),
    path('delete-account/',DeleteCurrentUserView.as_view(),name="delete_account"),
    path("reset-account/",ResetAccountView.as_view(),name="reset-account"),
    path("update-currency/",UpdateCurrencyView.as_view(),name="update-currency")
]