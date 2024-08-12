from django.urls import path
from . import views

urlpatterns = [
    path('create_category/',views.CreateCategoryAPIView.as_view(),name='create_category'),
    path('categories/',views.CategoriesListAPIView.as_view(),name='categories'),
    path('categories/<int:pk>',views.RetrieveUpdateDestroyCategoryAPIView.as_view(),name='single_category'),
    path('create_type/',views.CreateTypeAPIView.as_view(),name='create_type'),
    path('types',views.TypesListAPIView.as_view(),name="types"),
    path('types/<int:pk>',views.RetrieveUpdateDestroyTypeAPIView.as_view(),name='single_type'),
    path('create_transaction/',views.CreateTransactionAPIView.as_view(),name='create_transaction'),
    path('',views.TransactionsListAPIView.as_view(),name='transactions'),
    path('<int:pk>',views.RetrieveUpdateDestroyTransactionAPIView.as_view(),name='single_transaction')
]
