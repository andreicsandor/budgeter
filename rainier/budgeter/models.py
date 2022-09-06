from django.db import models

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