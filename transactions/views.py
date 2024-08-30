from rest_framework import generics
from .models import Categories,Types,Transactions
from .serializers import CategorySerializer,TypeSerializer,TransactionSerializer,TransactionReadSerializer
from rest_framework.permissions import AllowAny
from django.utils import timezone

#Categories
class CreateCategoryAPIView(generics.CreateAPIView):
    queryset=Categories.objects.all()
    serializer_class=CategorySerializer
    permission_classes=[AllowAny]


class CategoriesListAPIView(generics.ListAPIView):
    queryset=Categories.objects.all()
    serializer_class=CategorySerializer
    permission_classes=[AllowAny]


class RetrieveUpdateDestroyCategoryAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Categories.objects.all()
    serializer_class=CategorySerializer
    permission_classes=[AllowAny]


#Types
class CreateTypeAPIView(generics.CreateAPIView):
    queryset=Types.objects.all()
    serializer_class=TypeSerializer
    permission_classes=[AllowAny]


class TypesListAPIView(generics.ListAPIView):
    queryset=Types.objects.all()
    serializer_class=TypeSerializer
    permission_classes=[AllowAny]


class RetrieveUpdateDestroyTypeAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Types.objects.all()
    serializer_class=TypeSerializer
    permission_classes=[AllowAny]


#Transactions
class CreateTransactionAPIView(generics.CreateAPIView):
    queryset=Transactions.objects.all()
    serializer_class=TransactionSerializer
    permission_classes=[AllowAny]

    #def perform_create(self, serializer):
        #serializer.save(user=self.request.user)


class TransactionsListAPIView(generics.ListAPIView):
    serializer_class=TransactionReadSerializer
    permission_classes=[AllowAny]

    def get_queryset(self):
        queryset=Transactions.objects.all()
        time=self.request.query_params.get('time')

        current_time=timezone.now()
        
        if time=='year':
            queryset=queryset.filter(date__year=current_time.year)
        elif time=='month':
            queryset=queryset.filter(date__month=current_time.month)

        return queryset


class RetrieveUpdateDestroyTransactionAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Transactions.objects.all()
    serializer_class=TransactionSerializer
    permission_classes=[AllowAny]


class IncomeTransactionsAPIView(TransactionsListAPIView):
    serializer_class=TransactionReadSerializer
    permission_classes=[AllowAny]
    
    def get_queryset(self):
        queryset=super().get_queryset()
        return queryset.filter(type__category__name='Income')
    

class ExpenseTransactionsAPIView(TransactionsListAPIView):
    serializer_class=TransactionReadSerializer
    permission_classes=[AllowAny]

    def get_queryset(self):
        queryset=super().get_queryset()
        return queryset.filter(type__category__name='Expense')