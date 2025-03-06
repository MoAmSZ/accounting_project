from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('financial-report/', views.financial_report, name='financial_report'),
    path('expense-analysis/', views.expense_analysis, name='expense_analysis'),
    path('income-analysis/', views.income_analysis, name='income_analysis'),
]

