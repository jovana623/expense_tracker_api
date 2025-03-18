from rest_framework import generics
from transactions.models import Transactions
from transactions.serializers import TransactionSerializer,TransactionReadSerializer
from rest_framework.permissions import IsAuthenticated
from transactions.pagination import CustomPageNumberPagination
from django.utils import timezone
from django.db.models import Q,Sum
from rest_framework.views import APIView
from django.core.cache import cache
from rest_framework.response import Response
 

class CreateTransactionAPIView(generics.CreateAPIView):
    queryset=Transactions.objects.all()
    serializer_class=TransactionSerializer
    permission_classes=[IsAuthenticated]

    def perform_create(self, serializer):
        transaction = serializer.save(user=self.request.user)
        return transaction


class TransactionsListAPIView(generics.ListAPIView): 
    serializer_class=TransactionReadSerializer
    permission_classes=[IsAuthenticated]
    pagination_class=CustomPageNumberPagination
   
    def get_queryset(self):
        time=self.request.query_params.get('time')
        filter_month=self.request.query_params.get('month')
        sort_by=self.request.query_params.get('sortBy') 
        search=self.request.query_params.get('search')
        type=self.request.query_params.get('type')
        
        queryset = Transactions.objects.filter(user=self.request.user).select_related("user", "type").prefetch_related("type__category")

        if filter_month: 
            year,month=map(int,filter_month.split('-'))
            queryset=queryset.filter(date__month=month,date__year=year)
        elif time:
            current_time=timezone.now()
            if time=='year':
                queryset=queryset.filter(date__year=current_time.year)
            elif time=='month':
                queryset=queryset.filter(date__month=current_time.month,date__year=current_time.year)

        if sort_by=='name':
            queryset=queryset.order_by('name')
        elif sort_by=='amount-desc':
            queryset=queryset.order_by("-amount")
        elif sort_by=='amount-asc':
            queryset=queryset.order_by("amount")
        elif sort_by=="date-desc":
            queryset=queryset.order_by("-date")
        elif sort_by=="date-asc":
            queryset=queryset.order_by("date")

        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))

        if type:
            queryset=queryset.filter(type__id=type)

        return queryset


class RetrieveUpdateDestroyTransactionAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Transactions.objects.all()
    serializer_class=TransactionSerializer
    permission_classes=[IsAuthenticated]


class IncomeTransactionsAPIView(TransactionsListAPIView):
    serializer_class=TransactionReadSerializer
    permission_classes=[IsAuthenticated] 
    
    def get_queryset(self):
        queryset=super().get_queryset()
        return queryset.filter(type__category__name='Income')
    

class ExpenseTransactionsAPIView(TransactionsListAPIView):
    serializer_class=TransactionReadSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        queryset=super().get_queryset()
        return queryset.filter(type__category__name='Expense')
    

class TypeByMonthAPIView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request):
        user = self.request.user
        type_name=self.request.query_params.get("type")
        queryset=Transactions.objects.all()

        cache_key = f"user_{user.id}_monthly_spending_{type_name}"
        cached_data=cache.get(cache_key)

        if cached_data:
            return Response(cached_data)
        
        queryset = Transactions.objects.filter(user=user)

        if(type_name):
            queryset=queryset.filter(type__name=type_name)
        
        monthly_spending=(
            queryset
            .values('type__name','date__year','date__month')
            .annotate(total=Sum('amount'))
            .order_by('date__year','date__month','type__name')
            )
        
        cache.set(cache_key,list(monthly_spending),timeout=60*60*24)
        
        return Response(list(monthly_spending))
