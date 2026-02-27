from django.contrib import admin
from products.models import Category, Product, Brand, Supplier, Unit


# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    ...

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    ...

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    ...

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation']