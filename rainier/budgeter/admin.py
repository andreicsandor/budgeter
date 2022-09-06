from django.contrib import admin

from budgeter.models import Category, Currency, Type

# Register your models here.

admin.site.register(Category)
admin.site.register(Currency)
admin.site.register(Type)