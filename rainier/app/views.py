import datetime

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .forms import SignUpForm, LoginForm, UserForm, ProfileForm, TransactionForm
from .models import Profile, Currency, Type, Category, Transaction


# Create your views here.

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('.')
    elif request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/setup')
    else:
        form = SignUpForm()
    context = {
        "form": form
    }

    return render(request, "forms/signup.html", context)


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
def account_view(request):
    """
    Displays the account management page.
    """
    user = User.objects.get(pk=request.user.id)
    form = UserForm(instance=user)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            return redirect('/')
    context = {
        "form": form
    }

    return render(request, "forms/account.html", context)


@login_required
def preferences_view(request):
    """
    Displays the preferences page.
    """
    user = User.objects.get(pk=request.user.id)
    profile = Profile.objects.get(user=user)
    form = ProfileForm(instance=profile)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            return redirect('/account')
    context = {
        "form": form
    }

    return render(request, "forms/preferences.html", context)


@login_required
def home_view(request):
    """
    Displays all entries for the current user.
    """
    transactions = get_user_data(request)
    expenses, income = group_data(transactions)
    currency_short, currency_symbol = get_user_currency(request)
    query = finder(request)

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

    # Returns the user's balance
    balance = 0
    for entry in expenses:
        balance -= entry.amount
    for entry in income:
        balance += entry.amount

    # Computes the expenses & income for the current month
    expenses_current = 0
    income_current = 0
    day_current = datetime.datetime.now()
    month_current = day_current.strftime("%B") 

    for entry in expenses:
        if Transaction.TransactionMonth(entry) == month_current:
            expenses_current += entry.amount
    for entry in income:
        if Transaction.TransactionMonth(entry) == month_current:
            income_current += entry.amount

    # Computes the expenses & income relative to the total cash-flows
    try:
        expenses_relative = round(expenses_current / (expenses_current + income_current), 2) * 100
    except ZeroDivisionError:
        expenses_relative = 0  
    try:
        income_relative = round(income_current / (expenses_current + income_current), 2) * 100
    except ZeroDivisionError:
        income_relative = 0

    # Computes the expenses & income for the previous 6 months
    months_previous = []
    month_current_first = day_current.replace(day=1)

    for i in range(6):
        month_previous_first = (month_current_first - datetime.timedelta(days=1)).replace(day=1)
        month_current_first = month_previous_first
        months_previous.append(month_current_first.strftime("%B"))

    expenses_previous = dict.fromkeys(months_previous, 0)
    for month in months_previous:
        for entry in expenses:
            if Transaction.TransactionMonth(entry) == month:
                expenses_previous[month] += entry.amount
    
    income_previous = dict.fromkeys(months_previous, 0)
    for month in months_previous:
        for entry in income:
            if Transaction.TransactionMonth(entry) == month:
                income_previous[month] += entry.amount

    # Generates the chart data for the expenses overview
    labels_current = [Category.CategoryName(category) for category in categories_expenses]
    data_expenses_current = dict.fromkeys(labels_current, 0)
    
    for entry in expenses:
        if month_current == Transaction.TransactionMonth(entry):
            category = Transaction.TransactionCategory(entry).replace(" ", "")[1:]
            data_expenses_current[category] += entry.amount

    for key, value in dict(data_expenses_current).items():
        if value == 0:
            del data_expenses_current[key]

    labels_current = list(data_expenses_current.keys())
    values_expenses_current = list(data_expenses_current.values())

    # Generates the chart data for the previous expenses overview
    labels_previous = list(income_previous.keys())
    values_expenses_previous = list(expenses_previous.values())
    values_income_previous = list(income_previous.values())

    context = {
        "transactions": query,
        "currency_short": currency_short,
        "currency_symbol": currency_symbol,
        "types": types,
        "categories_expenses": categories_expenses,
        "categories_income": categories_income,
        "balance": balance,
        "summary_daily": summary_daily,
        "month_current": month_current,
        "expenses_current": expenses_current,
        "income_current": income_current,
        "expenses_previous": expenses_previous,
        "income_previous": income_previous,
        "expenses_relative": expenses_relative,
        "income_relative": income_relative,
        "labels_current": labels_current,
        "values_expenses_current": values_expenses_current,
        "labels_previous": labels_previous,
        "values_expenses_previous": values_expenses_previous,
        "values_income_previous": values_income_previous
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