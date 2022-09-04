from django import forms
from app.models import User, Profile, Currency, Transaction, Category, Type


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs = {"type": "text", "class": "form-control", "placeholder": "Username"}))
    password = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs = {"class": "form-control", "placeholder": "••••••••"}))