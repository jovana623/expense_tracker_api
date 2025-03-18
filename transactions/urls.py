from django.urls import path
from . import views

urlpatterns = [
    #categories
    path('create_category/',views.CreateCategoryAPIView.as_view(),name='create_category'),
    path('categories/',views.CategoriesListAPIView.as_view(),name='categories'),
    path('categories/<int:pk>',views.RetrieveUpdateDestroyCategoryAPIView.as_view(),name='single_category'),
    #types
    path('create_type/',views.CreateTypeAPIView.as_view(),name='create_type'),
    path('types/',views.TypesListAPIView.as_view(),name="types"),
    path('types/<int:pk>',views.RetrieveTypeAPIView.as_view(),name='single_type'),
    path("types/<int:pk>/update/", views.UpdateDestroyTypeAPIView.as_view(), name="update_destroy_type"), 
    #transactions
    path('create_transaction/',views.CreateTransactionAPIView.as_view(),name='create_transaction'),
    path('',views.TransactionsListAPIView.as_view(),name='transactions'),
    path('<int:pk>',views.RetrieveUpdateDestroyTransactionAPIView.as_view(),name='single_transaction'),
    path('income/',views.IncomeTransactionsAPIView.as_view(),name='income_transactions'),
    path('expense/',views.ExpenseTransactionsAPIView.as_view(),name='expense_transactions'),
    path('spending/month/',views.TypeByMonthAPIView.as_view(),name='category_month'),
    #budget
    path('budget/create/',views.CreateBudgetAPIView.as_view(),name='create_budget'), 
    path('budget/',views.BudgetListAPIView.as_view(),name='budget'),
    path('budget/<int:pk>',views.RetrieveUpdateDestroyBudgetAPIView.as_view(),name='single_budget'),
    #balance
    path('daily-balances/',views.DailyBalancesView.as_view(),name="daily_balance"),
    path('monthly-balances/',views.MonthlyBalance.as_view(),name='monthly_balances'),
    #stats
    path('dashboard/',views.DashboardAPIView.as_view(),name="dashboard_data"),
    path('statistics/',views.StatisticsAPIView.as_view(),name='statistics'),
]
   