from rest_framework import generics
from .models import Categories,Types,Transactions,Budget
from .serializers import CategorySerializer,TypeSerializer,TransactionSerializer,TransactionReadSerializer,TypeReadSerializer,BudgetSerializer,BudgetReadSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.utils import timezone
from django.db.models import Q,Min,Max
from .pagination import CustomPageNumberPagination
from rest_framework.views import APIView
from django.db.models import Sum,Avg,Case, When, F, DecimalField
from rest_framework.response import Response
from django.db.models.functions import TruncMonth
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from users.permissions import IsStuffUser
from django.core.cache import cache


#Categories
class CreateCategoryAPIView(generics.CreateAPIView):
    queryset=Categories.objects.all()
    serializer_class=CategorySerializer
    permission_classes=[AllowAny]


class CategoriesListAPIView(generics.ListAPIView):
    serializer_class=CategorySerializer
    permission_classes=[AllowAny]

    def get_queryset(self):
        cache_key="categories_list"
        cached_data=cache.get(cache_key)

        if cached_data is not None:
            return cached_data
        
        queryset=Categories.objects.all()
        cache.set(cache_key,queryset,timeout=60*60*24)
        return queryset
 

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
    serializer_class=TypeReadSerializer
    permission_classes=[AllowAny]
 
    def get_queryset(self):
        cache_key="types_list"
        cached_data=cache.get(cache_key)

        if cached_data:
            return cached_data
        
        queryset=Types.objects.all().select_related("category")
        serializer=TypeReadSerializer(queryset,many=True)
        serialized_data=serializer.data
        cache.set(cache_key,serialized_data,timeout=60*60*24)
        return serialized_data


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
        cache.delete(f"income_summary_{transaction.user.id}")
        cache.delete(f"expense_summary_{transaction.user_id}")


class TransactionsListAPIView(generics.ListAPIView): 
    serializer_class=TransactionReadSerializer
    permission_classes=[IsAuthenticated]
    pagination_class=CustomPageNumberPagination
   
    def get_queryset(self):
        time=self.request.query_params.get('time')
        filter_month=self.request.query_params.get('month')
        sort_by=self.request.query_params.get('sortBy') 
        search=self.request.query_params.get('search')
        
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

        return queryset


class RetrieveUpdateDestroyTransactionAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Transactions.objects.all()
    serializer_class=TransactionSerializer
    permission_classes=[IsAuthenticated]

    def perform_update(self, serializer):
        transaction=serializer.save()
        cache.delete(f"income_summary_{transaction.user.id}")
        cache.delete(f"expense_summary_{transaction.user_id}")

    def perform_destroy(self, instance):
        user_id=instance.user.id
        instance.delete()
        cache.delete(f"income_summary_{user_id}")
        cache.delete(f"expense_summary_{user_id}")


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



class IncomeSummaryAPIView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request):
        user_id=request.user.id
        cache_key = f"income_summary_{user_id}"
        cached_data=cache.get(cache_key)

        if cached_data:
            return Response(cached_data)
        
        monthly_income = (
            Transactions.objects
            .select_related('type','type__category')
            .filter(user=request.user, type__category__name='Income')
            .values('date__year', 'date__month')
            .annotate(total=Sum('amount'))
            .order_by('date__year', 'date__month')
        )
 
        yearly_income=(
            Transactions.objects
            .select_related('type','type__category')
            .filter(user=request.user, type__category__name='Income')
            .values('date__year')
            .annotate(total=Sum('amount'))
            .order_by('date__year')
        )

        data={
            "monthly_income": list(monthly_income),
            "yearly_income": list(yearly_income),
        }

        cache.set(cache_key,data,timeout=60*10)

        return Response(data)
    

class ExpenseSummaryAPIView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request):
        user_id=request.user.id
        cache_key = f"expense_summary_{user_id}"
        cached_data=cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        monthly_expense=(
            Transactions.objects
            .select_related('type','type__category')
            .filter(user=request.user,type__category__name="Expense")
            .values('date__year','date__month')
            .annotate(total=Sum('amount'))
            .order_by('date__year','date__month')
        )

        yearly_expense=(
            Transactions.objects
            .select_related('type', 'type__category')
            .filter(user=request.user,type__category__name='Expense')
            .values('date__year')
            .annotate(total=Sum('amount'))
            .order_by('date__year')
        )

        data={
            "monthly_expense": list(monthly_expense),
            "yearly_expense": list(yearly_expense),
        }

        cache.set(cache_key,data,timeout=10*60)

        return Response(data)
    

class CategoryByMonthAPIView(APIView):
    permission_classes=[IsAuthenticated]

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
    

#Budget
class CreateBudgetAPIView(generics.CreateAPIView):
    serializer_class=BudgetSerializer
    permission_classes=[IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ListBudgetAPIView(generics.ListAPIView):
    serializer_class=BudgetSerializer
    permission_classes=[AllowAny]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)


class RetrieveUpdateDestroyBudgetAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Budget.objects.all()
    serializer_class=BudgetSerializer
    permission_classes=[IsAuthenticated]


class BudgetList(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request):
        current_time=timezone.now()
        budgets=Budget.objects.filter(user=self.request.user)
        budget_data=[] 

        transactions = Transactions.objects.filter(
            user=self.request.user,
            date__year=current_time.year
        )

        for budget in budgets:
            if budget.period=='Yearly':
                transactions=Transactions.objects.filter(
                    type=budget.type,
                    date__year=current_time.year,
                    user=self.request.user
                )
            else:
                transactions=Transactions.objects.filter(
                    type=budget.type,
                    date__year=current_time.year,
                    date__month=current_time.month,
                    user=self.request.user
                )

            total_spent=transactions.aggregate(total=Sum('amount'))['total'] or 0
            percentage_used = (total_spent / budget.amount) * 100 if budget.amount > 0 else 0

            transaction_list = transactions.values(
                'id', 'name', 'amount', 'date', 'description'
            )

            serialized_budget=BudgetReadSerializer(budget).data

            budget_data.append({
                **serialized_budget,
                "total": total_spent,
                "percentage": percentage_used,
                "transactions": list(transaction_list)
            })

        return Response(budget_data)


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

