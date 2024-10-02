from rest_framework import generics
from .models import Categories,Types,Transactions
from .serializers import CategorySerializer,TypeSerializer,TransactionSerializer,TransactionReadSerializer,TypeReadSerializer
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.db.models import Q
from .pagination import CustomPageNumberPagination
from rest_framework.views import APIView
from django.db.models import Sum,Avg
from rest_framework.response import Response


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
    serializer_class=TypeReadSerializer
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
    pagination_class=CustomPageNumberPagination

    def get_queryset(self):
        queryset = Transactions.objects.all()
        time=self.request.query_params.get('time')
        filter_month=self.request.query_params.get('month')
        sort_by=self.request.query_params.get('sortBy')
        search=self.request.query_params.get('search')

        if filter_month:
            year,month=map(int,filter_month.split('-'))
            queryset=queryset.filter(date__month=month,date__year=year)
        elif time:
            current_time=timezone.now()
            if time=='year':
                queryset=queryset.filter(date__year=current_time.year)
            elif time=='month':
                queryset=queryset.filter(date__month=current_time.month)

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


class IncomeSummaryAPIView(APIView):
    permission_classes=[AllowAny]

    def get(self,request):
        monthly_income = (
            Transactions.objects
            .filter(type__category__name='Income')
            .values('date__year', 'date__month')
            .annotate(total=Sum('amount'))
            .order_by('date__year', 'date__month')
        )

        yearly_income=(
            Transactions.objects
            .filter(type__category__name='Income')
            .values('date__year')
            .annotate(total=Sum('amount'))
            .order_by('date__year')
        )

        return Response({
            "monthly_income": list(monthly_income),
            "yearly_income": list(yearly_income),
        })
    

class ExpenseSummaryAPIView(APIView):
    permission_classes=[AllowAny]

    def get(self,request):
        monthly_expense=(
            Transactions.objects
            .filter(type__category__name="Expense")
            .values('date__year','date__month')
            .annotate(total=Sum('amount'))
            .order_by('date__year','date__month')
        )

        yearly_expense=(
            Transactions.objects
            .filter(type__category__name='Expense')
            .values('date__year')
            .annotate(total=Sum('amount'))
            .order_by('date__year')
        )

        return Response({
            "monthly_expense": list(monthly_expense),
            "yearly_expense": list(yearly_expense),
        })
    

class CategoryByMonthAPIView(APIView):
    permission_classes=[AllowAny]

    def get(self,request):
        type_name=self.request.query_params.get("type")
        queryset=Transactions.objects.all()

        if(type_name):
            queryset=queryset.filter(type__name=type_name)

        monthly_spending=(
            queryset
            .values('type__name','date__year','date__month')
            .annotate(total=Sum('amount'))
            .order_by('date__year','date__month','type__name')
            )
        
        return Response(list(monthly_spending))


class StatisticsAPIView(TransactionsListAPIView):
    def get(self,request,*args,**kwargs):
        querysetIncome=self.get_queryset().filter(type__category__name='Income')
        querysetExpense=self.get_queryset().filter(type__category__name='Expense')
        
        top_income = querysetIncome.order_by('-amount').first()
        avg_income=querysetIncome.aggregate(avg_income=Avg('amount'))

        top_income_types=(querysetIncome
        .values('type__name')
        .annotate(total_amount=Sum('amount'))
        .order_by('-total_amount')[:4]
        )

        top_expense_types=(querysetExpense
        .values('type__name')
        .annotate(total_amount=Sum('amount'))
        .order_by('-total_amount')[:3]
        )
        

        top_expense = querysetExpense.order_by('-amount').first()
        avg_expense=querysetExpense.aggregate(avg_expense=Avg('amount'))

        return Response({
            "top_income": {
                "name": top_income.name if top_income else None,
                "amount": top_income.amount if top_income else None,
                "date": top_income.date if top_income else None,
            },
            "avg_income": avg_income["avg_income"],
            "top_expense": {
                "name": top_expense.name if top_expense else None,
                "amount": top_expense.amount if top_expense else None,
                "date": top_expense.date if top_expense else None,
            },
            "avg_expense": avg_expense["avg_expense"],
            "top_income_types":list(top_income_types),
            "top_expense_types":list(top_expense_types)
        })