from django.contrib import admin

from .models import Profile, Currency, Transaction, Type, Category 


# Register your models here.

admin.site.register(Profile)
admin.site.register(Currency)
admin.site.register(Transaction)
admin.site.register(Type)
admin.site.register(Category)