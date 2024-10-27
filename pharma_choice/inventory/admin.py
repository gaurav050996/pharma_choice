from django.contrib import admin
from .models import Category, Drug, Stock, UserOrder

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'category_name')

@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = ('drug_id', 'drug_name', 'category', 'price', 'discount', 'stock_status')

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('stock_id', 'drug', 'available_stock', 'stock_updated_on', 'stock_status')
    list_editable = ('available_stock',)

@admin.register(UserOrder)
class UserOrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'order_date', 'drug', 'quantity', 'price', 'total_amount')
