from rest_framework import generics
from transactions.models import Transactions,Budget
from transactions.serializers import BudgetSerializer,BudgetReadSerializer
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q,Sum
from rest_framework.views import APIView
from django.core.cache import cache
from rest_framework.response import Response


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

