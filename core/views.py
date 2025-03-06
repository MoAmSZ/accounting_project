from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from django.http import JsonResponse
from .models import Category, Transaction, Account, SavingGoal
from .forms import CategoryForm, TransactionForm, AccountForm, SavingGoalForm

def get_categories(request):
    """API endpoint برای دریافت دسته‌بندی‌ها بر اساس نوع"""
    category_type = request.GET.get('type')
    if category_type not in ['income', 'expense']:
        return JsonResponse({'error': 'نوع دسته‌بندی نامعتبر است'}, status=400)
    
    categories = Category.objects.filter(type=category_type).values('id', 'name', 'icon', 'color')
    return JsonResponse(list(categories), safe=False)

def dashboard(request):
    # آمار کلی
    accounts = Account.objects.filter(is_active=True)
    total_balance = sum(account.current_balance() for account in accounts)
    
    # تراکنش‌های اخیر
    recent_transactions = Transaction.objects.all().order_by('-date')[:5]
    
    # اهداف پس‌انداز فعال
    active_goals = SavingGoal.objects.filter(status='active')
    
    context = {
        'accounts': accounts,
        'total_balance': total_balance,
        'recent_transactions': recent_transactions,
        'active_goals': active_goals,
    }
    return render(request, 'core/dashboard.html', context)

def account_list(request):
    accounts = Account.objects.all()
    return render(request, 'core/account_list.html', {'accounts': accounts})

def account_add(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'حساب با موفقیت ایجاد شد.')
            return redirect('core:account_list')
    else:
        form = AccountForm()
    return render(request, 'core/account_form.html', {'form': form})

def account_edit(request, pk):
    account = get_object_or_404(Account, pk=pk)
    if request.method == 'POST':
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, 'حساب با موفقیت ویرایش شد.')
            return redirect('core:account_list')
    else:
        form = AccountForm(instance=account)
    return render(request, 'core/account_form.html', {'form': form})

def account_delete(request, pk):
    account = get_object_or_404(Account, pk=pk)
    account.delete()
    messages.success(request, 'حساب با موفقیت حذف شد.')
    return redirect('core:account_list')

def transaction_list(request):
    transactions = Transaction.objects.all()
    accounts = Account.objects.filter(is_active=True)
    categories = Category.objects.all()

    # فیلتر متنی
    q = request.GET.get('q')
    if q:
        transactions = transactions.filter(
            Q(description__icontains=q) |
            Q(account__name__icontains=q) |
            Q(category__name__icontains=q)
        )

    # فیلتر نوع تراکنش
    transaction_type = request.GET.get('type')
    if transaction_type:
        transactions = transactions.filter(type=transaction_type)

    # فیلتر حساب
    account_id = request.GET.get('account')
    if account_id:
        transactions = transactions.filter(
            Q(account_id=account_id) |
            Q(related_account_id=account_id)
        )

    # فیلتر دسته‌بندی
    category_id = request.GET.get('category')
    if category_id:
        transactions = transactions.filter(category_id=category_id)

    # فیلتر تاریخ
    date_from = request.GET.get('date_from')
    if date_from:
        transactions = transactions.filter(date__gte=date_from)

    date_to = request.GET.get('date_to')
    if date_to:
        transactions = transactions.filter(date__lte=date_to)

    # مرتب‌سازی بر اساس تاریخ
    transactions = transactions.order_by('-date')

    context = {
        'transactions': transactions,
        'accounts': accounts,
        'categories': categories,
    }
    return render(request, 'core/transaction_list.html', context)

def transaction_add(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تراکنش با موفقیت ثبت شد.')
            return redirect('core:transaction_list')
    else:
        initial = {}
        if request.GET.get('account'):
            initial['account'] = request.GET.get('account')
        if request.GET.get('category'):
            initial['category'] = request.GET.get('category')
        form = TransactionForm(initial=initial)
    return render(request, 'core/transaction_form.html', {'form': form})

def transaction_edit(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, 'تراکنش با موفقیت ویرایش شد.')
            return redirect('core:transaction_list')
    else:
        form = TransactionForm(instance=transaction)
    return render(request, 'core/transaction_form.html', {'form': form})

def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    transaction.delete()
    messages.success(request, 'تراکنش با موفقیت حذف شد.')
    return redirect('core:transaction_list')

def category_list(request):
    income_categories = Category.objects.filter(type='income')
    expense_categories = Category.objects.filter(type='expense')
    return render(request, 'core/category_list.html', {
        'income_categories': income_categories,
        'expense_categories': expense_categories,
    })

def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'دسته‌بندی با موفقیت ایجاد شد.')
            return redirect('core:category_list')
    else:
        form = CategoryForm()
    return render(request, 'core/category_form.html', {'form': form})

def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'دسته‌بندی با موفقیت ویرایش شد.')
            return redirect('core:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'core/category_form.html', {'form': form})

def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'دسته‌بندی با موفقیت حذف شد.')
    return redirect('core:category_list')

def saving_goal_list(request):
    goals = SavingGoal.objects.all()
    return render(request, 'core/saving_goal_list.html', {'goals': goals})

def saving_goal_add(request):
    if request.method == 'POST':
        form = SavingGoalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'هدف پس‌انداز با موفقیت ایجاد شد.')
            return redirect('core:saving_goal_list')
    else:
        form = SavingGoalForm()
    return render(request, 'core/saving_goal_form.html', {'form': form})

def saving_goal_edit(request, pk):
    goal = get_object_or_404(SavingGoal, pk=pk)
    if request.method == 'POST':
        form = SavingGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'هدف پس‌انداز با موفقیت ویرایش شد.')
            return redirect('core:saving_goal_list')
    else:
        form = SavingGoalForm(instance=goal)
    return render(request, 'core/saving_goal_form.html', {'form': form})
