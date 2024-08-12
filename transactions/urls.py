from django.urls import path
from .views import CreateCategoryAPIView,CategoriesListAPIView,RetrieveUpdateDestroyCategoryAPIView


urlpatterns = [
    path('create_category/',CreateCategoryAPIView.as_view(),name='create_category'),
    path('categories/',CategoriesListAPIView.as_view(),name='categories'),
    path('categories/<int:pk>',RetrieveUpdateDestroyCategoryAPIView.as_view(),name='single_category')
]
