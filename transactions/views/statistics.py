from transactions.models import Transactions
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q,Sum,Case,When,IntegerField,Value,Avg
from rest_framework.views import APIView
from django.core.cache import cache
from rest_framework.response import Response
from transactions.views import TransactionsListAPIView

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
    


