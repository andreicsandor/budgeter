from django.db import models

from django.contrib.auth.models import User

from budgeter.models import Currency

# Create your models here.

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