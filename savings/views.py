from rest_framework import generics
from .models import Savings,Payments
from .serializers import SavingSerializer,PaymentsSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from rest_framework.response import Response
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


@receiver(post_save,sender=Payments)
@receiver(post_delete,sender=Payments)
def clear_cache_on_payment_change(sender,instance,**kwargs):
    saving=instance.saving.id
    cache_key = f"saving_{saving}_payments"
    cache.delete(cache_key)
    
    saving_cache_key = f"user_{instance.saving.user.id}_savings"
    cache.delete(saving_cache_key)


@receiver(post_save,sender=Savings)
@receiver(post_delete,sender=Savings)
def clear_cache_on_saving_change(sender,instance,**kwargs):
    cache_key=f"user_{instance.user.id}_savings"
    cache.delete(cache_key)

#Savings
class CreateSavingAPIView(generics.CreateAPIView):
    queryset=Savings.objects.all()
    serializer_class=SavingSerializer
    permission_classes=[IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        

class ListSavingsAPIView(generics.ListAPIView):
    serializer_class = SavingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        cache_key = f"user_{user.id}_savings"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data
        
        queryset = Savings.objects.filter(user=user).select_related("user")
        serialized_data = SavingSerializer(queryset, many=True).data
        cache.set(cache_key, serialized_data, timeout=60 * 60)
        return queryset


class RetrieveUpdateDestroySavingAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Savings.objects.all()
    serializer_class=SavingSerializer
    permission_classes=[IsAuthenticated]
    

#Payments
class CreatePaymentAPIView(generics.CreateAPIView):
    queryset=Payments.objects.all()
    serializer_class=PaymentsSerializer
    permission_classes=[IsAuthenticated]


class ListPaymentAPIView(generics.ListAPIView):
    serializer_class = PaymentsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        saving_id = self.request.query_params.get("saving")
        cache_key = f"saving_{saving_id}_payments"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data
        
        queryset = Payments.objects.filter(saving_id=saving_id)
        serialized_data = PaymentsSerializer(queryset, many=True).data
        cache.set(cache_key, serialized_data, timeout=60 * 60) 

        return serialized_data 

    def list(self, request, *args, **kwargs):
        return Response(self.get_queryset())


class RetrieveUpdateDestroyPaymentAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Payments.objects.all()
    serializer_class=PaymentsSerializer
    permission_classes=[IsAuthenticated]


