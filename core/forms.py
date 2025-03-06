from django import forms
from .models import Category, Transaction, SavingGoal, Account

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'type', 'icon', 'color']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['date', 'type', 'category', 'account', 'amount', 'description', 'related_account']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تنظیم اولیه فیلدها
        self.fields['category'].queryset = Category.objects.none()  # ابتدا خالی
        self.fields['account'].queryset = Account.objects.filter(is_active=True)
        self.fields['related_account'].queryset = Account.objects.filter(is_active=True)
        self.fields['related_account'].required = False
        
        # اضافه کردن کلاس‌های Bootstrap
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        # تنظیم فیلدها بر اساس نوع تراکنش
        transaction_type = None
        if self.instance.pk:  # اگر در حال ویرایش هستیم
            transaction_type = self.instance.type
        elif 'type' in self.data:  # اگر فرم ارسال شده
            transaction_type = self.data.get('type')
        elif 'type' in self.initial:  # اگر مقدار اولیه داریم
            transaction_type = self.initial.get('type')
            
        if transaction_type:
            if transaction_type == 'transfer':
                self.fields['category'].required = False
                self.fields['related_account'].required = True
            else:
                self.fields['category'].required = True
                self.fields['related_account'].required = False
                # فیلتر دسته‌بندی‌ها بر اساس نوع تراکنش
                self.fields['category'].queryset = Category.objects.filter(type=transaction_type)
    
    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('type')
        category = cleaned_data.get('category')
        related_account = cleaned_data.get('related_account')
        account = cleaned_data.get('account')
        
        if transaction_type == 'transfer':
            if not related_account:
                raise forms.ValidationError('برای تراکنش انتقالی باید حساب مقصد را مشخص کنید.')
            if related_account == account:
                raise forms.ValidationError('حساب مبدا و مقصد نمی‌توانند یکسان باشند.')
        else:
            if not category:
                raise forms.ValidationError('برای تراکنش‌های درآمد و هزینه باید دسته‌بندی را مشخص کنید.')
            
            # بررسی تطابق نوع تراکنش با نوع دسته‌بندی
            if transaction_type == 'income' and category.type != 'income':
                raise forms.ValidationError('برای تراکنش درآمد باید از دسته‌بندی درآمد استفاده کنید.')
            elif transaction_type == 'expense' and category.type != 'expense':
                raise forms.ValidationError('برای تراکنش هزینه باید از دسته‌بندی هزینه استفاده کنید.')
        
        return cleaned_data
#
# class BudgetForm(forms.ModelForm):
#     class Meta:
#         model = Budget
#         fields = ['category', 'amount', 'period', 'start_date', 'end_date']
#         widgets = {
#             'start_date': forms.DateInput(attrs={'type': 'date'}),
#             'end_date': forms.DateInput(attrs={'type': 'date'}),
#         }

class SavingGoalForm(forms.ModelForm):
    class Meta:
        model = SavingGoal
        fields = ['title', 'target_amount', 'current_amount', 'deadline', 'description']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'account_type', 'account_number', 'bank_name', 
                 'initial_balance', 'description', 'is_active']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['account_number'].required = False
        self.fields['bank_name'].required = False 