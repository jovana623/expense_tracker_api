from django.urls import path
from . import views

urlpatterns = [
    path('create_category/',views.CreateCategoryAPIView.as_view(),name='create_category'),
    path('categories/',views.CategoriesListAPIView.as_view(),name='categories'),
    path('categories/<int:pk>',views.RetrieveUpdateDestroyCategoryAPIView.as_view(),name='single_category'),
    path('create_type/',views.CreateTypeAPIView.as_view(),name='create_type'),
    path('types',views.TypesListAPIView.as_view(),name="types"),
    path('types/<int:pk>',views.RetrieveUpdateDestroyTypeAPIView.as_view(),name='single_type'),
    path('create_transaction/',views.CreateTransactionAPIView.as_view(),name='create_transaction'),
    path('',views.TransactionsListAPIView.as_view(),name='transactions'),
    path('<int:pk>',views.RetrieveUpdateDestroyTransactionAPIView.as_view(),name='single_transaction'),
    path('income/',views.IncomeTransactionsAPIView.as_view(),name='income_transactions'),
    path('expense/',views.ExpenseTransactionsAPIView.as_view(),name='expense_transactions'),
    path('income/monthly/',views.IncomeSummaryAPIView.as_view(),name='monthly_income'),
    path('expense/monthly/',views.ExpenseSummaryAPIView.as_view(),name='monthly_expenses'),
    path('spending/month/',views.CategoryByMonthAPIView.as_view(),name='category_month'),
    path('statistics/',views.StatisticsAPIView.as_view(),name='statistics'),
    path('budget/create/',views.CreateBudgetAPIView.as_view(),name='create_budget'),
    path('budget/',views.ListBudgetAPIView.as_view(),name='budget'),
    path('budget/<int:pk>',views.RetrieveUpdateDestroyBudgetAPIView.as_view(),name='single_budget'),
    path('budget/used/',views.BudgetList.as_view(),name='used_budget')
]
