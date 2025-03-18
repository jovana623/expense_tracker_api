from rest_framework import generics
from transactions.models import Types
from transactions.serializers import TypeReadSerializer,TypeSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.permissions import AllowAny
from users.permissions import IsStuffUser
from django.core.cache import cache

class CreateTypeAPIView(generics.CreateAPIView):
    queryset=Types.objects.all()
    serializer_class=TypeSerializer
    permission_classes=[IsStuffUser]

    def perform_create(self, serializer):
        instance=serializer.save()
        cache.delete("types_list")
        return instance


class UpdateDestroyTypeAPIView(generics.UpdateAPIView,generics.DestroyAPIView):
    queryset=Types.objects.all()
    serializer_class=TypeSerializer
    permission_classes=[IsStuffUser]

    def perform_update(self, serializer):
        instance=serializer.save()
        cache.delete("types_list")
        return instance
    
    def perform_destroy(self, instance):
        instance.delete()
        cache.delete("types_list")


class TypesListAPIView(generics.ListAPIView):
    queryset = Types.objects.all()
    serializer_class=TypeReadSerializer
    permission_classes=[AllowAny]

    @method_decorator(cache_page(60*60*24,key_prefix="types_list"))
    def list(self,request,*args,**kwargs):
        return super().list(request, *args, **kwargs)


class RetrieveTypeAPIView(generics.RetrieveAPIView):
    queryset = Types.objects.all()
    serializer_class = TypeSerializer
    permission_classes = [AllowAny]
 