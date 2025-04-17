from transactions.models import Transactions
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q,Sum,Case,When,IntegerField,Value,Avg
from rest_framework.views import APIView
from django.core.cache import cache
from rest_framework.response import Response
from transactions.views import TransactionsListAPIView

class DashboardSummaryAPIView(TransactionsListAPIView):
    pagination_class=None

    def list(self, request, *args, **kwargs):
        queryset=self.get_queryset()

        total_income=queryset.filter(type__category__name="Income").aggregate(
            total=Sum("amount")
        )["total"] or 0

        total_expense=queryset.filter(type__category__name="Expense").aggregate(
            total=Sum("amount")
        )["total"] or 0

        return Response({
            "total_income":total_income,
            "total_expense":total_expense
        })


class DashboardHistoryAPIView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request):
        queryset = Transactions.objects.filter(user=request.user).select_related("type", "type__category")

        transactions = (
            queryset
            .values("date__year", "date__month")
            .annotate(
                total_income=Sum(
                    Case(
                        When(type__category__name="Income", then="amount"),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                ),
                total_expense=Sum(
                    Case(
                        When(type__category__name="Expense", then="amount"),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                ),
            )
            .order_by("date__year", "date__month")
        )

        monthly_data = [
            {
                "month": f"{transaction['date__year']}-{str(transaction['date__month']).zfill(2)}",
                "total_income": transaction["total_income"],
                "total_expense": transaction["total_expense"],
            }
            for transaction in transactions if transaction["date__month"] is not None
        ]

        yearly_data = {}
        for transaction in transactions:
            year = transaction["date__year"]
            if year not in yearly_data:
                yearly_data[year] = {"total_income": 0, "total_expense": 0}
            yearly_data[year]["total_income"] += transaction["total_income"]
            yearly_data[year]["total_expense"] += transaction["total_expense"]

        yearly_data_list = [
            {
                "year": year,
                "total_income": yearly_data[year]["total_income"],
                "total_expense": yearly_data[year]["total_expense"],
            }
            for year in yearly_data
        ]

        return Response({
            "monthly_data": monthly_data,
            "yearly_data": yearly_data_list,
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
    


