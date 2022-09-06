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

    def CurrencyDetails(self):
        """Returns the currency details."""
        return self.abbreviation, self.symbol

    def CurrencyList(self):
        """Retrieves the available currency types."""
        return self.objects.all().order_by('name')

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

    def TypeList(self):
        """Retrieves the available transaction types."""
        return self.objects.all().order_by('name')

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

    def CategoryList(self):
        """Retrieves the available transaction categories."""
        categories_expenses = self.objects.filter(type="1").order_by('name')
        categories_income = self.objects.filter(type="2").order_by('name')
        return categories_expenses, categories_income

    def CategoryType(self):
        """Returns the category type formatted as a string."""
        return str(self.type)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'