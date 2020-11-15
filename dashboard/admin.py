from django.contrib import admin
from .models import Order, Product, Transaction

# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    pass

class ProductAdmin(admin.ModelAdmin):
    list_display = ('code', 'description')

class TransactionAdmin(admin.ModelAdmin):
    pass

admin.site.register(Order, OrderAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Transaction, TransactionAdmin)