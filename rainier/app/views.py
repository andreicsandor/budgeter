import datetime

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .forms import LoginForm, TransactionForm
from .models import Profile, Currency, Type, Category, Transaction


# Create your views here.

def login_view(request):
    if request.user.is_authenticated:
        return redirect('.')
    elif request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('/')
    else:
        form = LoginForm()
    context = {
        "form": form
    }

    return render(request, "forms/login.html", context)


def logout_view(request):
    logout(request)

    return redirect('/')


@login_required
def home_view(request):
    """
    Displays all entries for the current user.
    """
    transactions = get_user_data(request)
    expenses, income = group_data(transactions)
    currency_short, currency_symbol = get_user_currency(request)
    query = finder(request)

    # Returns the user's balance
    balance = 0
    for entry in expenses:
        balance -= entry.amount
    for entry in income:
        balance += entry.amount

    # Returns the available categories
    types = Type.objects.all().order_by('name')
    categories_expenses = Category.objects.filter(type="1").order_by('name')
    categories_income = Category.objects.filter(type="2").order_by('name')
   
    # Counts the no. of transactions per day & computes the daily amount
    days = list(dict.fromkeys([item.date for item in query]))
    counter_daily = dict.fromkeys(days, 0)
    balance_daily = dict.fromkeys(days, 0)

    for day in days:
        for entry in query:
            if entry.date == day:
                counter_daily[day] += 1
                if entry in expenses:
                    balance_daily[day] -= round(float(entry.amount), 2)
                if entry in income:
                    balance_daily[day] += round(float(entry.amount), 2)    

    # Creates a dicitonary containing each day with corresponding statistics
    statistics = []
    
    for count, total in zip(counter_daily.values(), balance_daily.values()):
        pair = [count, total]
        statistics.append(pair)

    summary_daily = dict(zip(days, statistics))

    context = {
        "transactions": query,
        "currency_short": currency_short,
        "currency_symbol": currency_symbol,
        "types": types,
        "categories_expenses": categories_expenses,
        "categories_income": categories_income,
        "balance": balance,
        "summary_daily": summary_daily,
    }

    return render(request, "home.html", context)


@login_required
def create_view(request):
    """
    Creates a new transaction entry.
    """
    currency_short, currency_symbol = get_user_currency(request)

    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = User.objects.get(pk=request.user.id)
            obj.save()
            return redirect('/')
    else:
        form = TransactionForm()
    context = {
        "form": form,
        "currency_short": currency_short,
        "currency_symbol": currency_symbol
    }

    return render(request, "forms/create.html", context)


@login_required
def edit_view(request, pk):
    """
    Edit an existing transaction entry.
    """
    currency_short, currency_symbol = get_user_currency(request)

    entry = Transaction.objects.get(id=pk)
    form = TransactionForm(instance=entry)

    if request.method == "POST":
        form = TransactionForm(request.POST, instance=entry)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            return redirect('/')
    context = {
        "form": form,
        "id": pk,
        "currency_short": currency_short,
        "currency_symbol": currency_symbol
    }

    return render(request, "forms/edit.html", context)


@login_required
def delete_view(request, pk):
    """
    Delete an existing transaction entry.
    """
    entry = Transaction.objects.get(id=pk)

    if request.method == "POST":
        entry.delete()
        return redirect('/')
    context = {
        "id": pk
    }

    return render(request, "forms/delete.html", context)


def categories_view(request):
    """
    Loads the corresponding categories for each type of transaction in the create entry window.
    """
    type_id = request.GET.get('type_id')
    categories = Category.objects.filter(type_id=type_id).all()

    return render(request, 'dropdowns/categories.html', {'categories': categories})


# Other functions 


@login_required
def get_user_data(request):
    """
    Returns the user's set of entries.
    """
    user = User.objects.get(pk=request.user.id)
    data = Transaction.objects.filter(user=user).order_by('-date', '-amount', 'name')

    return data


@login_required
def get_user_currency(request):
    user = User.objects.get(pk=request.user.id)
    try:
        currency = Profile.ProfileCurrency(Profile.objects.get(user=user))
        short = Currency.CurrencyShort(currency)
        symbol = Currency.CurrencySymbol(currency)
    except Profile.DoesNotExist:
        short = ""
        symbol = ""

    return short, symbol


def group_data(data):
    """
    Groups the user's entries into expenses & income.
    """
    expenses = data.filter(type="1").order_by('-amount')
    income = data.filter(type="2").order_by('-amount')

    return expenses, income


@login_required
def finder(request):
    """
    Returns the corresponding query set for the search & filter features.
    """
    qs = get_user_data(request)

    return qs