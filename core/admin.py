from django.contrib import admin
from .models import Category, Transaction, Account, SavingGoal

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'icon', 'color']
    list_filter = ['type']
    search_fields = ['name']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'type', 'account', 'get_target', 'amount']
    list_filter = ['type', 'account', 'category']
    search_fields = ['description']
    date_hierarchy = 'date'
    
    def get_target(self, obj):
        if obj.type in ['transfer_in', 'transfer_out']:
            return obj.related_account.name
        return obj.category.name if obj.category else '-'
    get_target.short_description = 'دسته‌بندی/حساب مقصد'

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'account_type', 'bank_name', 'current_balance', 'is_active']
    list_filter = ['account_type', 'is_active']
    search_fields = ['name', 'bank_name', 'account_number']

@admin.register(SavingGoal)
class SavingGoalAdmin(admin.ModelAdmin):
    list_display = ['title', 'target_amount', 'current_amount', 'deadline', 'status']
    list_filter = ['status']
    search_fields = ['title']
