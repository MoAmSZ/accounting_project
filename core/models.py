from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Account(models.Model):
    ACCOUNT_TYPES = (
        ('cash', 'نقدی'),
        ('bank', 'حساب بانکی'),
        ('card', 'کارت بانکی'),
        ('digital', 'کیف پول دیجیتال'),
    )
    
    name = models.CharField(max_length=100, verbose_name="نام حساب")
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='cash', verbose_name="نوع حساب")
    account_number = models.CharField(max_length=50, blank=True, verbose_name="شماره حساب/کارت")
    bank_name = models.CharField(max_length=50, blank=True, verbose_name="نام بانک")
    initial_balance = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="موجودی اولیه")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def current_balance(self):
        # محاسبه موجودی فعلی با در نظر گرفتن همه تراکنش‌ها
        income = Transaction.objects.filter(
            account=self, 
            type='income'
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        expense = Transaction.objects.filter(
            account=self, 
            type='expense'
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        # محاسبه انتقال‌ها
        transfer_out = Transaction.objects.filter(
            account=self,
            type='transfer'
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        transfer_in = Transaction.objects.filter(
            related_account=self,
            type='transfer'
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        return self.initial_balance + income - expense - transfer_out + transfer_in
    
    def __str__(self):
        if self.account_type in ['bank', 'card']:
            return f"{self.name} - {self.bank_name}"
        return self.name
    
    class Meta:
        verbose_name = "حساب"
        verbose_name_plural = "حساب‌ها"

class Category(models.Model):
    CATEGORY_TYPES = (
        ('income', 'درآمد'),
        ('expense', 'هزینه'),
    )
    
    name = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    type = models.CharField(max_length=20, choices=CATEGORY_TYPES, verbose_name="نوع دسته‌بندی")
    icon = models.CharField(max_length=50, default='money', verbose_name="آیکون")
    color = models.CharField(max_length=20, default='#000000', verbose_name="رنگ")
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
    
    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('income', 'درآمد'),
        ('expense', 'هزینه'),
        ('transfer', 'انتقال'),
    )
    
    date = models.DateField(default=timezone.now, verbose_name="تاریخ")
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='expense', verbose_name="نوع تراکنش")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="دسته‌بندی", null=True, blank=True)
    account = models.ForeignKey(Account, on_delete=models.PROTECT, verbose_name="حساب", related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="مبلغ")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    
    # برای تراکنش‌های انتقالی
    related_account = models.ForeignKey(Account, on_delete=models.PROTECT, null=True, blank=True, 
                                      verbose_name="حساب مقصد", related_name='related_transactions')
    
    def save(self, *args, **kwargs):
        # کم کردن مبلغ از حساب مبدا و اضافه کردن به حساب مقصد برای انتقال
        if self.type == 'transfer':
            if not self.related_account:
                raise ValueError('برای تراکنش انتقالی باید حساب مقصد را مشخص کنید.')
            if self.related_account == self.account:
                raise ValueError('حساب مبدا و مقصد نمی‌توانند یکسان باشند.')
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        if self.type == 'transfer':
            return f"انتقال به {self.related_account} - {self.amount:,} تومان"
        return f"{self.date} - {self.get_type_display()} - {self.amount:,} تومان"
    
    class Meta:
        verbose_name = "تراکنش"
        verbose_name_plural = "تراکنش‌ها"
        ordering = ['-date', '-id']

class SavingGoal(models.Model):
    GOAL_STATUS = (
        ('active', 'فعال'),
        ('achieved', 'محقق شده'),
        ('cancelled', 'لغو شده'),
    )
    
    title = models.CharField(max_length=200, verbose_name="عنوان هدف")
    target_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="مبلغ هدف")
    current_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="مبلغ فعلی")
    deadline = models.DateField(verbose_name="مهلت")
    status = models.CharField(max_length=20, choices=GOAL_STATUS, default='active', verbose_name="وضعیت")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    
    def progress_percentage(self):
        return (self.current_amount / self.target_amount) * 100 if self.target_amount > 0 else 0
    
    def __str__(self):
        return f"{self.title} - {self.target_amount:,} ریال"
    
    class Meta:
        verbose_name = "هدف پس‌انداز"
        verbose_name_plural = "اهداف پس‌انداز"

class TransactionLine(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='lines', verbose_name="تراکنش")
    account = models.ForeignKey(Account, on_delete=models.PROTECT, verbose_name="حساب")
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="بدهکار")
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="بستانکار")
    description = models.CharField(max_length=200, blank=True, verbose_name="توضیحات")

    def __str__(self):
        return f"{self.transaction.reference_number} - {self.account.name}"

    class Meta:
        verbose_name = "سطر تراکنش"
        verbose_name_plural = "سطرهای تراکنش"

class Invoice(models.Model):
    INVOICE_TYPES = (
        ('sale', 'فاکتور فروش'),
        ('purchase', 'فاکتور خرید'),
    )
    
    INVOICE_STATUS = (
        ('draft', 'پیش‌نویس'),
        ('confirmed', 'تایید شده'),
        ('cancelled', 'لغو شده'),
    )
    
    number = models.CharField(max_length=50, unique=True, verbose_name="شماره فاکتور")
    type = models.CharField(max_length=20, choices=INVOICE_TYPES, verbose_name="نوع فاکتور")
    date = models.DateField(default=timezone.now, verbose_name="تاریخ")
    due_date = models.DateField(null=True, blank=True, verbose_name="تاریخ سررسید")
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default='draft', verbose_name="وضعیت")
    customer_name = models.CharField(max_length=200, verbose_name="نام مشتری/فروشنده")
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="مبلغ کل")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="ایجاد کننده")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.number} - {self.customer_name}"

    class Meta:
        verbose_name = "فاکتور"
        verbose_name_plural = "فاکتورها"

class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='lines', verbose_name="فاکتور")
    description = models.CharField(max_length=200, verbose_name="شرح")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="تعداد")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="قیمت واحد")
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="مبلغ")

    def __str__(self):
        return f"{self.invoice.number} - {self.description}"

    class Meta:
        verbose_name = "سطر فاکتور"
        verbose_name_plural = "سطرهای فاکتور"
