from transactions.models import Transactions
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q,Sum,Min,Max,Case,When,F,DecimalField
from rest_framework.views import APIView
from django.core.cache import cache
from rest_framework.response import Response
from datetime import datetime,timedelta
from django.db.models.functions import TruncMonth
from dateutil.relativedelta import relativedelta 

class DailyBalancesView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request,*args,**kwargs):
        user_id = request.user.id
        month_param=request.query_params.get("month")

        cache_key = f"daily_balances_{user_id}_{month_param}"
        cached_data=cache.get(cache_key)

        if cached_data:
            return Response(cached_data)
        
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
            
        cache.set(cache_key, daily_balances, timeout=60*60)

        return Response(daily_balances)


class MonthlyBalance(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request,*args,**kwargs):
        user_id = request.user.id
        time=request.query_params.get("time")
        month=request.query_params.get("month")

        cache_key = f"monthly_balance_{user_id}_time_{time}_month_{month}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

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
            
        cache.set(cache_key, monthly_balances, timeout=60*60)
        return Response(monthly_balances)

