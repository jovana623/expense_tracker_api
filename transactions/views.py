from rest_framework import generics
from .models import Categories,Types
from .serializers import CategorySerializer,TypeSerializer
from rest_framework.permissions import IsAuthenticated


class CreateCategoryAPIView(generics.CreateAPIView):
    queryset=Categories.objects.all()
    serializer_class=CategorySerializer
    permission_classes=[IsAuthenticated]


class CategoriesListAPIView(generics.ListAPIView):
    queryset=Categories.objects.all()
    serializer_class=CategorySerializer
    permission_classes=[IsAuthenticated]


class RetrieveUpdateDestroyCategoryAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Categories.objects.all()
    serializer_class=CategorySerializer
    permission_classes=[IsAuthenticated]


class CreateTypeAPIView(generics.CreateAPIView):
    queryset=Types.objects.all()
    serializer_class=TypeSerializer
    permission_classes=[IsAuthenticated]


class TypesListAPIView(generics.ListAPIView):
    queryset=Types.objects.all()
    serializer_class=TypeSerializer
    permission_classes=[IsAuthenticated]


class RetrieveUpdateDestroyTypeAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Types.objects.all()
    serializer_class=TypeSerializer
    permission_classes=[IsAuthenticated]