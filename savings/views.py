from rest_framework import generics
from .models import Savings,Payments
from .serializers import SavingSerializer,PaymentsSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated



#Savings
class CreateSavingAPIView(generics.CreateAPIView):
    queryset=Savings.objects.all()
    serializer_class=SavingSerializer
    permission_classes=[IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ListSavingsAPIView(generics.ListAPIView):
    queryset=Savings.objects.all()
    serializer_class=SavingSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        return Savings.objects.filter(user=self.request.user)

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
    queryset=Payments.objects.all()
    serializer_class=PaymentsSerializer
    permission_classes=[IsAuthenticated]


class RetrieveUpdateDestroyPaymentAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Payments.objects.all()
    serializer_class=PaymentsSerializer
    permission_classes=[IsAuthenticated]


