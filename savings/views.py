from rest_framework import generics
from .models import Savings,Payments
from .serializers import SavingSerializer,PaymentsSerializer
from rest_framework.permissions import AllowAny



#Savings
class CreateSavingAPIView(generics.CreateAPIView):
    queryset=Savings.objects.all()
    serializer_class=SavingSerializer
    permission_classes=[AllowAny]
    
    #def perform_create(self, serializer):
        #serializer.save(user=self.request.user)


class ListSavingsAPIView(generics.ListAPIView):
    queryset=Savings.objects.all()
    serializer_class=SavingSerializer
    permission_classes=[AllowAny]


class RetrieveUpdateDestroySavingAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Savings.objects.all()
    serializer_class=SavingSerializer
    permission_classes=[AllowAny]
 


#Payments
class CreatePaymentAPIView(generics.CreateAPIView):
    queryset=Payments.objects.all()
    serializer_class=PaymentsSerializer
    permission_classes=[AllowAny]


class ListPaymentAPIView(generics.ListAPIView):
    queryset=Payments.objects.all()
    serializer_class=PaymentsSerializer
    permission_classes=[AllowAny]


class RetrieveUpdateDestroyPaymentAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Payments.objects.all()
    serializer_class=PaymentsSerializer
    permission_classes=[AllowAny]


