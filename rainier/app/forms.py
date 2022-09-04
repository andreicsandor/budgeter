from django import forms
from django.contrib.auth.forms import UserChangeForm
from app.models import User, Profile, Currency, Transaction, Category, Type


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


class TransactionForm(forms.ModelForm):
    type = forms.ModelChoiceField(queryset=Type.objects.all(), empty_label="Select type...", widget=forms.Select(attrs = {"class" : "form-select"}))
    name = forms.CharField(widget=forms.TextInput(attrs = {"type": "text", "class": "form-control", "placeholder": "Name"}))
    amount = forms.DecimalField(min_value=0, max_digits=11, decimal_places=2, widget=forms.NumberInput(attrs = {"type": "number", "class": "form-control", "placeholder": "Amount"}))
    date = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y', attrs = {"class": "form-control", "id": "input-date", "name": "input-date"}))
    category = forms.ModelChoiceField(queryset=Type.objects.all(), empty_label="Select category...", widget=forms.Select(attrs = {"class" : "form-select"}))
    note = forms.CharField(required=False, widget=forms.TextInput(attrs = {"type": "text", "class": "form-control", "placeholder": "Note"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.none()

        if 'type' in self.data:
            try:
                type_id = int(self.data.get('type'))
                self.fields['category'].queryset = Category.objects.filter(type_id=type_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['category'].queryset = self.instance.type.category_set.order_by('name')

    class Meta:
        model = Transaction
        fields = ('type', 'name', 'amount', 'date',  'category', 'note')