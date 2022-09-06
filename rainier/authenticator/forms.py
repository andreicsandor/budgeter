from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import User

from authenticator.models import Profile
from budgeter.models import Currency


class SignUpForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs = {"type": "text", "class": "form-control", "placeholder": "Username"}))
    first_name = forms.CharField(widget=forms.TextInput(attrs = {"type": "text", "class": "form-control", "placeholder": "First Name"}))
    last_name = forms.CharField(widget=forms.TextInput(attrs = {"type": "text", "class": "form-control", "placeholder": "Last Name"}))
    email = forms.EmailField(max_length=200, widget=forms.EmailInput(attrs = {"type": "email", "class": "form-control", "placeholder": "jappleseed@mail.com"}))
    password1 = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs = {"class": "form-control", "placeholder": "••••••••"}))
    password2 = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs = {"class": "form-control", "placeholder": "••••••••"}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs = {"type": "text", "class": "form-control", "placeholder": "Username"}))
    password = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs = {"class": "form-control", "placeholder": "••••••••"}))


class UserForm(UserChangeForm):
    username = forms.CharField(widget=forms.TextInput(attrs = {"type": "text", "class": "form-control", "placeholder": "Username"}))
    first_name = forms.CharField(widget=forms.TextInput(attrs = {"type": "text", "class": "form-control", "placeholder": "First Name"}))
    last_name = forms.CharField(widget=forms.TextInput(attrs = {"type": "text", "class": "form-control", "placeholder": "Last Name"}))
    email = forms.EmailField(max_length=200, widget=forms.EmailInput(attrs = {"type": "email", "class": "form-control", "placeholder": "jappleseed@mail.com"}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class ProfileForm(forms.ModelForm):
    currency = forms.ModelChoiceField(queryset=Currency.objects.all(), empty_label="Pick your prefered currency...", widget=forms.Select(attrs = {"class" : "form-select"}))

    class Meta:
        model = Profile
        fields = ('currency',)