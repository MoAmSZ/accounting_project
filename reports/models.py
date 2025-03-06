from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from core.models import Account, Category, Transaction

class ReportPeriod(models.Model):
    """دوره زمانی گزارش"""
    PERIOD_CHOICES = [
        ('daily', 'روزانه'),
        ('weekly', 'هفتگی'),
        ('monthly', 'ماهانه'),
        ('quarterly', 'سه ماهه'),
        ('yearly', 'سالانه'),
        ('custom', 'دلخواه'),
    ]

    title = models.CharField(max_length=100, verbose_name="عنوان")
    period_type = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='monthly', verbose_name="نوع دوره")
    start_date = models.DateField(verbose_name="تاریخ شروع")
    end_date = models.DateField(verbose_name="تاریخ پایان")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    description = models.TextField(blank=True, verbose_name="توضیحات")

    class Meta:
        verbose_name = "دوره گزارش"
        verbose_name_plural = "دوره‌های گزارش"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_period_type_display()})"

    def clean(self):
        """اعتبارسنجی تاریخ‌ها"""
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("تاریخ شروع نمی‌تواند بعد از تاریخ پایان باشد.")

    def get_duration(self):
        """محاسبه مدت دوره به روز"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

class FinancialReport(models.Model):
    """گزارش مالی"""
    REPORT_TYPES = [
        ('income', 'گزارش درآمد'),
        ('expense', 'گزارش هزینه'),
        ('cash_flow', 'گزارش جریان نقدی'),
        ('balance', 'گزارش تراز'),
    ]

    title = models.CharField(max_length=200, verbose_name="عنوان گزارش")
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, verbose_name="نوع گزارش")
    period = models.ForeignKey(ReportPeriod, on_delete=models.CASCADE, verbose_name="دوره گزارش")
    accounts = models.ManyToManyField(Account, verbose_name="حساب‌های بانکی")
    categories = models.ManyToManyField(Category, blank=True, verbose_name="دسته‌بندی‌ها")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "گزارش مالی"
        verbose_name_plural = "گزارش‌های مالی"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.get_report_type_display()}"

    def get_total_amount(self):
        """محاسبه مجموع مبلغ تراکنش‌ها"""
        transactions = Transaction.objects.filter(
            date__range=(self.period.start_date, self.period.end_date),
            account__in=self.accounts.all()
        )
        
        if self.categories.exists():
            transactions = transactions.filter(category__in=self.categories.all())
            
        if self.report_type == 'income':
            transactions = transactions.filter(type='income')
        elif self.report_type == 'expense':
            transactions = transactions.filter(type='expense')
            
        return transactions.aggregate(total=models.Sum('amount'))['total'] or 0

    def get_transaction_count(self):
        """تعداد تراکنش‌های گزارش"""
        transactions = Transaction.objects.filter(
            date__range=(self.period.start_date, self.period.end_date),
            account__in=self.accounts.all()
        )
        
        if self.categories.exists():
            transactions = transactions.filter(category__in=self.categories.all())
            
        if self.report_type == 'income':
            transactions = transactions.filter(type='income')
        elif self.report_type == 'expense':
            transactions = transactions.filter(type='expense')
            
        return transactions.count()

    def get_category_summary(self):
        """خلاصه تراکنش‌ها بر اساس دسته‌بندی"""
        transactions = Transaction.objects.filter(
            date__range=(self.period.start_date, self.period.end_date),
            account__in=self.accounts.all()
        )

        if self.report_type == 'income':
            transactions = transactions.filter(type='income')
        elif self.report_type == 'expense':
            transactions = transactions.filter(type='expense')

        return transactions.values('category__name').annotate(
            total=models.Sum('amount'),
            count=models.Count('id')
        ).order_by('-total')

class ReportChart(models.Model):
    """نمودارهای گزارش"""
    CHART_TYPES = [
        ('line', 'نمودار خطی'),
        ('bar', 'نمودار میله‌ای'),
        ('pie', 'نمودار دایره‌ای'),
        ('area', 'نمودار مساحت'),
    ]

    report = models.ForeignKey(FinancialReport, on_delete=models.CASCADE, verbose_name="گزارش مالی", related_name='charts')
    title = models.CharField(max_length=100, verbose_name="عنوان نمودار")
    chart_type = models.CharField(max_length=20, choices=CHART_TYPES, verbose_name="نوع نمودار")
    data_config = models.JSONField(verbose_name="تنظیمات داده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "نمودار گزارش"
        verbose_name_plural = "نمودارهای گزارش"
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.title} ({self.get_chart_type_display()})"

    def get_chart_data(self):
        """دریافت داده‌های نمودار"""
        return self.data_config