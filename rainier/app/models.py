import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import localtime

# Create your models here.

class Currency(models.Model):
    """
    Represents the preferred currency for transactions.
    """
    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=50)
    symbol = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.symbol} {self.name}, {self.abbreviation}"

    def CurrencyLong(self):
        name = str(self.name)
        return name

    def CurrencyShort(self):
        abbreviation = str(self.abbreviation)
        return abbreviation

    def CurrencySymbol(self):
        symbol = str(self.symbol)
        return symbol

    class Meta:
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'
    

class Profile(models.Model):
    """
    Adds custom fields to the parent user class.
    """
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user}"

    def ProfileCurrency(self):
        currency = self.currency
        return currency

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'


class Type(models.Model):
    """
    Represents the type of the transaction for the individual budget entries.
    """
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}"

    def TypeName(self):
        name = str(self.name)
        return name

    class Meta:
        verbose_name = 'Type'
        verbose_name_plural = 'Types'


class Category(models.Model):
    """
    Represents the categories for the individual budget entries.
    Both expenses and income categories are grouped together.
    """
    name = models.CharField(max_length=50)
    logo = models.CharField(max_length=50, default=None)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.logo} {self.name}"

    def CategoryName(self):
        name = str(self.name)
        return name

    def CategoryType(self):
        type = str(self.type)
        return type

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Transaction(models.Model):
    """
    Represents the individual budget entries that can be either 
    expenses or income streams.

    All types of transactions are grouped together and Custom Model 
    managers are used to filter between expenses and income.
    """
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    created = models.DateTimeField(default=localtime)
    date = models.DateField(default=datetime.date.today)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user} - {self.date} - {self.category}, {self.type} - {self.name}, {self.amount}USD"

    def TransactionMonth(self):
         month = self.date.strftime("%B")
         # day = self.date.strftime("%-d")
         # year = self.date.strftime("%Y")
         return month

    def TransactionName(self):
        name = str(self.name)
        return name

    def TransactionType(self):
        type = str(self.type)
        return type

    def TransactionCategory(self):
        category = str(self.category)
        return category

    def TransactionNote(self):
        note = str(self.note)
        return note

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'