# inventory/admin.py
from django.contrib import admin
from .models import Drug, Stock, Category, UserOrder

class StockAdmin(admin.ModelAdmin):
    list_display = ('stock_id', 'drug', 'available_stock', 'stock_updated_on', 'drug_stock_status')

    def drug_stock_status(self, obj):
        return obj.drug.stock_status
    drug_stock_status.short_description = 'In Stock'  # Customize column name in admin

admin.site.register(Category)
admin.site.register(Drug)
admin.site.register(Stock, StockAdmin)
admin.site.register(UserOrder)