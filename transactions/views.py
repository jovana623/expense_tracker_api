from rest_framework import generics
from .models import Categories,Types,Transactions,Budget
from .serializers import CategorySerializer,TypeSerializer,TransactionSerializer,TransactionReadSerializer,TypeReadSerializer,BudgetSerializer,BudgetReadSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.utils import timezone
from django.db.models import Q,Min,Max,Sum,Avg,Case, When, F, DecimalField,Value, IntegerField
from .pagination import CustomPageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models.functions import TruncMonth
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from users.permissions import IsStuffUser
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


#Categories
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

#Types
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


#Transactions
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
    

class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        time=self.request.query_params.get('time')
        month=self.request.query_params.get('month')

        current_year = timezone.now().year
        current_month = timezone.now().month

        transactions=(Transactions.objects
                    .filter(user=request.user)
                    .values("date__year","date__month")
                    .annotate(
                        total_income=Sum(
                            Case(
                                When(type__category__name="Income",then="amount"),
                                default=Value(0),
                                output_field=IntegerField()
                            )
                        ),
                        total_expense=Sum(
                            Case(
                                When(type__category__name="Expense",then="amount"),
                                default=Value(0),
                                output_field=IntegerField()
                            )
                        )
                    ).order_by('date__year','date__month')
                )
        monthly_data=[
            {
                "year": entry["date__year"],
                "month": entry["date__month"],
                "total_income": entry["total_income"],
                "total_expense": entry["total_expense"],
            }
            for entry in transactions if entry["date__month"] is not None
        ]
        yearly_data={}
        for entry in transactions:
            year=entry["date__year"]
            if year not in yearly_data:
                yearly_data[year]={"total_income":0,"total_expense":0} 
            yearly_data[year]["total_income"]+=entry["total_income"]
            yearly_data[year]["total_expense"]+=entry["total_expense"]

        yearly_data_list = [
            {"year": y, "total_income": yearly_data[y]["total_income"], "total_expense": yearly_data[y]["total_expense"]}
            for y in yearly_data
        ]

        total_income = 0  
        total_expense = 0 

        if time == "month":
            return Response(next((entry for entry in monthly_data if entry["year"] == current_year and entry["month"] == (int(month) if month else current_month)), {}))
        
        if time == "year":
            return Response(next((entry for entry in yearly_data_list if entry["year"] == current_year), {}))
        
        if month:
            selected_year, selected_month = map(int, month.split("-")) if "-" in month else (current_year, int(month))
            return Response(next((entry for entry in monthly_data if entry["year"] == selected_year and entry["month"] == selected_month), {}))

        if time == "all":
            total_income = sum(entry["total_income"] for entry in yearly_data_list)
            total_expense = sum(entry["total_expense"] for entry in yearly_data_list)

        return Response({
            "monthly_data": monthly_data, 
            "yearly_data": yearly_data_list,
            "total_income": total_income,
            "total_expense": total_expense
        })


class CategoryByMonthAPIView(APIView):
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


class StatisticsAPIView(TransactionsListAPIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        cache_key = f"user_{user.id}_statistics"

        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)


        queryset = self.get_queryset().filter(user=user).select_related("type").prefetch_related("type__category")

        top_income_query = queryset.filter(type__category__name="Income").order_by("-amount").values("name", "amount", "date")[:1]
        top_income = top_income_query.first() if top_income_query.exists() else {"name": None, "amount": None, "date": None}

        top_expense_query = queryset.filter(type__category__name="Expense").order_by("-amount").values("name", "amount", "date")[:1]
        top_expense = top_expense_query.first() if top_expense_query.exists() else {"name": None, "amount": None, "date": None}

        avg_stats = queryset.aggregate(
            avg_income=Avg("amount", filter=Q(type__category__name="Income")),
            avg_expense=Avg("amount", filter=Q(type__category__name="Expense")),
        )

        top_income_types = list(
            queryset.filter(type__category__name="Income")
            .values("type__name")
            .annotate(total_amount=Sum("amount"))
            .order_by("-total_amount")[:4]
        )

        top_expense_types = list(
            queryset.filter(type__category__name="Expense")
            .values("type__name")
            .annotate(total_amount=Sum("amount"))
            .order_by("-total_amount")[:3]
        )

        response_data = {
            "top_income": top_income,
            "avg_income": avg_stats["avg_income"],
            "top_expense": top_expense,
            "avg_expense": avg_stats["avg_expense"],
            "top_income_types": top_income_types,
            "top_expense_types": top_expense_types,
        }

        cache.set(cache_key, response_data, timeout=60 * 60 * 24) 

        return Response(response_data)
    

#Budget
class CreateBudgetAPIView(generics.CreateAPIView):
    serializer_class=BudgetSerializer
    permission_classes=[IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BudgetListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user=request.user
        current_time=timezone.now()

        cache_key=f"user_{user.id}_budgets"
        cached_data=cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        budgets=Budget.objects.filter(user=user).select_related("type")
        budget_data=[]

        for budget in budgets:
            transactions=Transactions.objects.filter(user=user,type=budget.type)

            if budget.period=='Yearly':
                transactions=transactions.filter(date__year=current_time.year)
            else:
                transactions=transactions.filter(date__year=current_time.year,date__month=current_time.month)
            
            total=transactions.aggregate(total=Sum('amount'))['total'] or 0
            percentage = (total / budget.amount) * 100 if budget.amount > 0 else 0

            serialized_budget=BudgetReadSerializer(budget).data
            budget_data.append({
                **serialized_budget,
                "total":total,
                "percentage":percentage
            })
        
        cache.set(cache_key,budget_data,timeout=60*60)
        return Response(budget_data)


class RetrieveUpdateDestroyBudgetAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Budget.objects.all()
    serializer_class=BudgetSerializer
    permission_classes=[IsAuthenticated]


#Balance
class DailyBalancesView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request,*args,**kwargs):
        user_transactions=Transactions.objects.filter(user=request.user)
        min_max_dates=user_transactions.aggregate(
            first_date=Min("date"),
            last_date=Max("date")
        )

        first_date=min_max_dates["first_date"]
        last_date=min_max_dates["last_date"]

        if not first_date or not last_date:
            return Response([])
        
        today=timezone.now().date()
        last_date=max(last_date,today)
        
        daily_totals=(
            user_transactions
            .values("date")
            .annotate(
                daily_income=Sum(
                    Case(
                        When(type__category__name="Income",then=F("amount")),
                        default=0,
                        output_field=DecimalField()
                    )
                ),
                daily_expense=Sum(
                    Case(
                        When(type__category__name="Expense",then=F("amount")),
                        default=0,
                        output_field=DecimalField()
                    )
                )
            )
            .order_by("date")
        )

        transactions_by_date={
            entry["date"]:entry for entry in daily_totals
        }

        current_date=first_date
        daily_balances=[]
        running_balance=0

        while current_date<=last_date:
            entry=transactions_by_date.get(current_date,{"daily_income":0,"daily_expense":0})

            income=entry["daily_income"] or 0
            expense=entry["daily_expense"] or 0

            daily_total=income-expense
            running_balance+=daily_total

            daily_balances.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "balance": running_balance
            })

            current_date += timedelta(days=1)

        
        
        month_param=request.query_params.get("month")
        

        if month_param:
            try:
                year,month=map(int,month_param.split('-'))
                daily_balances=[
                    balance for balance in daily_balances
                    if datetime.strptime(balance["date"], "%Y-%m-%d").year == year and
                    datetime.strptime(balance["date"], "%Y-%m-%d").month == month
                ]
            except ValueError:
                return Response({"error": "Month must be in the format YYYY-MM."}, status=400)

        return Response(daily_balances)


class MonthlyBalance(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request,*args,**kwargs):
        user_transactions = Transactions.objects.filter(user=request.user)
        min_max_dates=user_transactions.aggregate(
            first_date=Min("date"),
            last_date=Max("date")
        )

        first_date=min_max_dates["first_date"]
        last_date=min_max_dates["last_date"]

        if not first_date or not last_date:
            return Response([])
        
        monthly_totals=(
            user_transactions
            .annotate(
                month=TruncMonth('date')
            )
            .values("month")
            .annotate(
                monthly_income=Sum(
                    Case(
                        When(type__category__name="Income",then=F("amount")),
                        default=0,
                        output_field=DecimalField()
                        )
                ),
                monthly_expense=Sum(
                    Case(
                        When(type__category__name="Expense",then=F("amount")),
                        default=0,
                        output_field=DecimalField()
                    )
                )
            ).order_by("month")
        )

        transactions_by_month={entry["month"]:entry for entry in monthly_totals}

        current_month=first_date.replace(day=1)
        last_month=last_date.replace(day=1)

        monthly_balances=[]
        running_balance=0

        while current_month<=last_date:
            entry=transactions_by_month.get(current_month,{"monthly_income":0,"monthly_expense":0})

            income=entry["monthly_income"] or 0
            expense=entry["monthly_expense"] or 0
            monthly_total=income-expense
            running_balance+=monthly_total

            monthly_balances.append({
                "date": current_month.strftime("%Y-%m"),
                "balance": running_balance
            })

            current_month += relativedelta(months=1)

        time=request.query_params.get("time")
        month=request.query_params.get("month")

        current_year=datetime.now().year

        if (time=='year'):
            try:
                monthly_balances=[
                    balance for balance in monthly_balances
                    if datetime.strptime(balance["date"], "%Y-%m").year == current_year
            ]
            except ValueError:
                return Response({"Wrong format for a year"},status=400)
        
        if month:
            try:
                year, month_number = map(int, month.split('-'))
                monthly_balances = [
                    balance for balance in monthly_balances
                    if datetime.strptime(balance["date"], "%Y-%m").year == year and
                    datetime.strptime(balance["date"], "%Y-%m").month == month_number
                ]
            except ValueError:
                return Response({"error": "Month must be in the format YYYY-MM."}, status=400)

        return Response(monthly_balances)

