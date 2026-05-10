from django.contrib import admin
from .models import Budget, Expense, Profile, UserCard

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'income', 'income_category', 'expenses', 'balance', 'date')
    list_filter = ('income_category', 'date')
    search_fields = ('user__username', 'income_category')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'category', 'date', 'time_added')
    list_filter = ('category', 'date')
    search_fields = ('user__username', 'category')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'language', 'gender', 'date_registered')
    list_filter = ('language', 'gender')
    search_fields = ('user__username', 'full_name')

@admin.register(UserCard)
class UserCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_number', 'card_holder', 'expiry_date', 'card_type', 'date_added')
    list_filter = ('card_type', 'date_added')
    search_fields = ('user__username', 'card_holder', 'card_number')