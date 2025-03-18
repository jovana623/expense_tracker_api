from rest_framework import generics
from transactions.models import Categories
from transactions.serializers import CategorySerializer
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.permissions import AllowAny


class CreateCategoryAPIView(generics.CreateAPIView):
    queryset=Categories.objects.all()
    serializer_class=CategorySerializer
    permission_classes=[AllowAny]


class CategoriesListAPIView(generics.ListAPIView):
    queryset=Categories.objects.all()
    serializer_class=CategorySerializer
    permission_classes=[AllowAny]

    @method_decorator(cache_page(60*24, key_prefix="categories"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    
class RetrieveUpdateDestroyCategoryAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Categories.objects.all()
    serializer_class=CategorySerializer
    permission_classes=[AllowAny]
