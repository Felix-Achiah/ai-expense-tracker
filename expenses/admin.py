# expenses/admin.py
from django.contrib import admin
from .models import Expense

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'description', 'category', 'date')
    search_fields = ('description', 'category')
    list_filter = ('category', 'date')