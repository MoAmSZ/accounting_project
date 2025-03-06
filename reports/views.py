from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth, TruncYear
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .models import ReportPeriod, FinancialReport, ReportChart
from core.models import Transaction, Category, Account
import json

def financial_report(request):
    """نمایش گزارش مالی کلی"""
    # محاسبه آمار کلی
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    monthly_income = Transaction.objects.filter(
        type='income',
        date__range=(start_of_month, end_of_month)
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    monthly_expense = Transaction.objects.filter(
        type='expense',
        date__range=(start_of_month, end_of_month)
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # نمودار درآمد و هزینه ماهانه
    last_12_months = []
    for i in range(12):
        date = today - timedelta(days=30*i)
        month_start = date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        income = Transaction.objects.filter(
            type='income',
            date__range=(month_start, month_end)
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        expense = Transaction.objects.filter(
            type='expense',
            date__range=(month_start, month_end)
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        last_12_months.append({
            'month': month_start.strftime('%Y-%m'),
            'income': float(income) if isinstance(income, Decimal) else income,
            'expense': float(expense) if isinstance(expense, Decimal) else expense
        })
    
    last_12_months.reverse()
    
    # نمودار دایره‌ای هزینه‌ها بر اساس دسته‌بندی
    category_expenses = Transaction.objects.filter(
        type='expense',
        date__range=(start_of_month, end_of_month)
    ).values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # نمودار دایره‌ای درآمدها بر اساس دسته‌بندی
    category_incomes = Transaction.objects.filter(
        type='income',
        date__range=(start_of_month, end_of_month)
    ).values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Convert Decimal to float for JSON serialization
    category_expenses = [{
        'category__name': item['category__name'],
        'total': float(item['total']) if isinstance(item['total'], Decimal) else item['total']
    } for item in category_expenses]
    
    category_incomes = [{
        'category__name': item['category__name'],
        'total': float(item['total']) if isinstance(item['total'], Decimal) else item['total']
    } for item in category_incomes]
    
    context = {
        'monthly_income': float(monthly_income) if isinstance(monthly_income, Decimal) else monthly_income,
        'monthly_expense': float(monthly_expense) if isinstance(monthly_expense, Decimal) else monthly_expense,
        'monthly_balance': float(monthly_income - monthly_expense) if isinstance(monthly_income, Decimal) else (monthly_income - monthly_expense),
        'last_12_months': json.dumps(last_12_months),
        'category_expenses': category_expenses,
        'category_incomes': category_incomes,
    }
    
    return render(request, 'reports/financial_report.html', context)


def expense_analysis(request):
    """تحلیل هزینه‌ها"""
    # فیلتر تاریخ
    period = request.GET.get('period', 'month')
    today = timezone.now().date()
    
    if period == 'month':
        start_date = today.replace(day=1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    elif period == 'year':
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
    else:  # all time
        start_date = Transaction.objects.earliest('date').date
        end_date = today
    
    # تحلیل هزینه‌ها بر اساس دسته‌بندی
    category_analysis = Transaction.objects.filter(
        type='expense',
        date__range=(start_date, end_date)
    ).values('category__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # محاسبه درصد برای هر دسته‌بندی
    total_expense = sum(item['total'] for item in category_analysis)
    
    category_analysis = [{
        'category__name': item['category__name'],
        'total': float(item['total']) if isinstance(item['total'], Decimal) else item['total'],
        'count': item['count'],
        'percentage': float(item['total'] / total_expense * 100) if total_expense else 0
    } for item in category_analysis]
    
    # روند هزینه‌ها در طول زمان
    expense_trend = Transaction.objects.filter(
        type='expense',
        date__range=(start_date, end_date)
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')
    
    # Convert Decimal to float for JSON serialization
    expense_trend = [{
        'month': item['month'],
        'total': float(item['total']) if isinstance(item['total'], Decimal) else item['total']
    } for item in expense_trend]
    
    context = {
        'period': period,
        'category_analysis': category_analysis,
        'expense_trend': expense_trend,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'reports/expense_analysis.html', context)

def income_analysis(request):
    """تحلیل درآمدها"""
    # فیلتر تاریخ
    period = request.GET.get('period', 'month')
    today = timezone.now().date()
    
    if period == 'month':
        start_date = today.replace(day=1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    elif period == 'year':
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
    else:  # all time
        start_date = Transaction.objects.earliest('date').date
        end_date = today
    
    # تحلیل درآمدها بر اساس دسته‌بندی
    category_analysis = Transaction.objects.filter(
        type='income',
        date__range=(start_date, end_date)
    ).values('category__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # محاسبه درصد برای هر دسته‌بندی
    total_income = sum(item['total'] for item in category_analysis)
    
    # برای نمایش در جدول و نمودار، اعداد اصلی را نگه می‌داریم
    category_analysis = [{
        'category__name': item['category__name'],
        'total': float(item['total']) if isinstance(item['total'], Decimal) else item['total'],
        'count': item['count'],
        'percentage': float(item['total'] / total_income * 100) if total_income else 0
    } for item in category_analysis]
    
    # روند درآمدها در طول زمان
    income_trend = Transaction.objects.filter(
        type='income',
        date__range=(start_date, end_date)
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')
    
    # Convert Decimal to float for JSON serialization
    income_trend = [{
        'month': item['month'],
        'total': float(item['total']) if isinstance(item['total'], Decimal) else item['total']
    } for item in income_trend]
    
    context = {
        'period': period,
        'category_analysis': category_analysis,
        'income_trend': income_trend,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'reports/income_analysis.html', context)
