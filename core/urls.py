from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # حساب‌ها
    path('accounts/', views.account_list, name='account_list'),
    path('accounts/add/', views.account_add, name='account_add'),
    path('accounts/<int:pk>/edit/', views.account_edit, name='account_edit'),
    path('accounts/<int:pk>/delete/', views.account_delete, name='account_delete'),
    
    # تراکنش‌ها
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/add/', views.transaction_add, name='transaction_add'),
    path('transactions/<int:pk>/edit/', views.transaction_edit, name='transaction_edit'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
    
    # دسته‌بندی‌ها
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # اهداف پس‌انداز
    path('saving-goals/', views.saving_goal_list, name='saving_goal_list'),
    path('saving-goals/add/', views.saving_goal_add, name='saving_goal_add'),
    path('saving-goals/<int:pk>/edit/', views.saving_goal_edit, name='saving_goal_edit'),
    path('api/categories/', views.get_categories, name='api_categories'),
] 