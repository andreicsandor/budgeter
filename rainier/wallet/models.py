import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import localtime

from budgeter.models import Category, Type

# Create your models here.

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
        """Returns the formatted month of the transaction."""
        return self.date.strftime("%B")

    def TransactionType(self):
        """Returns the type of the transaction formatted as a string."""
        return str(self.type)

    def TransactionCategory(self):
        """Returns the category of the transaction formatted as a string."""
        return str(self.category)

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'