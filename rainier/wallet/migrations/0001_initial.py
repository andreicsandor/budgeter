# Generated by Django 4.0.6 on 2022-09-06 10:17

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('budgeter', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.localtime)),
                ('date', models.DateField(default=datetime.date.today)),
                ('name', models.CharField(max_length=50)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=11)),
                ('note', models.CharField(blank=True, max_length=255)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='budgeter.category')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='budgeter.type')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Transaction',
                'verbose_name_plural': 'Transactions',
            },
        ),
    ]