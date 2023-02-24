import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.views import View

from authenticator.models import Profile
from budgeter.models import Category, Type
from wallet.forms import TransactionForm
from wallet.models import Transaction
from wallet.services import finder, get_entries, group_entries

MONTH_INDEX = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

# Create your views here.

class Viewer(View):
    """
    Represents a child class for views. 

    Displays the entries, queries, user-specific statistics and 
    main forms through multiple screens.
    """

    @login_required 
    def dashboard(request):
        """Displays the corresponding entries & statistics for the current user."""

        # Prevents the user from skipping the initial configuration step.
        try:
            if Profile.objects.get(user=request.user.id):
                pass
        except ObjectDoesNotExist:
            return redirect('/configure')

        # Common data
        types = Type.TypeList(Type)
        categories_expenses, categories_income = Category.CategoryList(Category)

        # User-specific data
        profile = Profile.objects.get(user=request.user.id)
        currency_short, currency_symbol = Profile.ProfileCurrency(profile)
        entries = get_entries(request)
        expenses, income = group_entries(entries)

        # Filtered entries
        query = finder(request)
        
        # Computes the user's balance
        balance_total = 0
        for entry in expenses:
            balance_total -= entry.amount
        for entry in income:
            balance_total += entry.amount

        # Counts the no. of entries per day & computes the daily expenditure
        days = list(dict.fromkeys([item.date for item in query]))
        balance_daily = dict.fromkeys(days, 0)
        counter_daily = dict.fromkeys(days, 0)
        for day in days:
            for entry in query:
                if entry.date == day:
                    counter_daily[day] += 1
                    if entry in expenses:
                        balance_daily[day] -= round(float(entry.amount), 2)
                    if entry in income:
                        balance_daily[day] += round(float(entry.amount), 2)
        statistics = []
        for count, total in zip(counter_daily.values(), balance_daily.values()):
            pair = [count, total]
            statistics.append(pair)
        summary_daily = dict(zip(days, statistics))

        # Computes the absolute expenses & income for the current month
        expenses_current = 0
        income_current = 0

        day_current = datetime.datetime.now()
        month_current = day_current.strftime("%B")
        year_current = datetime.datetime.now().strftime("%Y")
        year_previous = str(datetime.datetime.now().year - 1)

        for entry in expenses:
            if Transaction.TransactionMonth(entry) == month_current and Transaction.TransactionYear(entry) == year_current:
                expenses_current += entry.amount
        for entry in income:
            if Transaction.TransactionMonth(entry) == month_current and Transaction.TransactionYear(entry) == year_current:
                income_current += entry.amount

        # Computes the relative expenses & income for the current month
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
        month_current_start = day_current.replace(day=1)
        for _ in range(6):
            months_previous_start = (month_current_start - datetime.timedelta(days=1)).replace(day=1)
            month_current_start = months_previous_start
            months_previous.append(month_current_start.strftime("%B"))

        expenses_previous = dict.fromkeys(months_previous, 0)
        income_previous = dict.fromkeys(months_previous, 0)
        
        # Covers the case when the previous 6 months are in the current year
        if months_previous == sorted(months_previous, key=MONTH_INDEX.index, reverse=True):  
            for month in months_previous:
                for entry in expenses:
                    if Transaction.TransactionMonth(entry) == month and Transaction.TransactionYear(entry) == year_current:
                        expenses_previous[month] += entry.amount
                for entry in income:
                    if Transaction.TransactionMonth(entry) == month and Transaction.TransactionYear(entry) == year_current:
                        income_previous[month] += entry.amount  

        # Covers the case when in the previous 6 months two years overlap
        else:
            for month in months_previous:
                for entry in expenses:
                    if month in ["January", "February", "March", "April", "May"]:
                        if Transaction.TransactionMonth(entry) == month and Transaction.TransactionYear(entry) == year_current:
                            expenses_previous[month] += entry.amount
                    else:
                        if Transaction.TransactionMonth(entry) == month and Transaction.TransactionYear(entry) == year_previous:
                            expenses_previous[month] += entry.amount
                for entry in income:
                    if month in ["January", "February", "March", "April", "May"]:
                        if Transaction.TransactionMonth(entry) == month and Transaction.TransactionYear(entry) == year_current:
                            income_previous[month] += entry.amount      
                    else:
                        if Transaction.TransactionMonth(entry) == month and Transaction.TransactionYear(entry) == year_previous:
                            income_previous[month] += entry.amount 

        # Generates the chart data for the current expenses overview
        labels_expenses_current = [category.name for category in categories_expenses]
        data_expenses_current = dict.fromkeys(labels_expenses_current, 0)
        for entry in expenses:
            if month_current == Transaction.TransactionMonth(entry):
                # Ignores the category logo
                category = Transaction.TransactionCategory(entry).replace(" ", "")[1:]
                data_expenses_current[category] += entry.amount
        for key, value in dict(data_expenses_current).items():
            if value == 0:
                del data_expenses_current[key]
        labels_expenses_current = list(data_expenses_current.keys())
        values_expenses_current = list(data_expenses_current.values())

        # Generates the chart data for the previous expenses overview
        labels_entries_previous = list(income_previous.keys())
        values_expenses_previous = list(expenses_previous.values())
        values_income_previous = list(income_previous.values())
        
        context = {
            "types": types,
            "categories_expenses": categories_expenses,
            "categories_income": categories_income,
            "currency_short": currency_short,
            "currency_symbol": currency_symbol,
            "entries": query,
            "balance_total": balance_total,
            "summary_daily": summary_daily,
            "month_current": month_current,
            "expenses_current": expenses_current,
            "income_current": income_current,
            "expenses_relative": expenses_relative,
            "income_relative": income_relative,
            "expenses_previous": expenses_previous,
            "income_previous": income_previous,
            "labels_expenses_current": labels_expenses_current,
            "values_expenses_current": values_expenses_current,
            "labels_entries_previous": labels_entries_previous,
            "values_expenses_previous": values_expenses_previous,
            "values_income_previous": values_income_previous
        }

        return render(request, "home.html", context)


    @login_required 
    def creator(request):
        """Creates a new transaction entry."""

        # Prevents the user from skipping the initial configuration step.
        try:
            if Profile.objects.get(user=request.user.id):
                pass
        except ObjectDoesNotExist:
            return redirect('/configure')

        # User-specific data
        profile = Profile.objects.get(user=request.user.id)
        currency_short, currency_symbol = Profile.ProfileCurrency(profile)

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

        return render(request, "create.html", context)


    @login_required 
    def editor(request, pk):
        """Edit an existing transaction entry."""

        # Prevents the user from skipping the initial configuration step.
        try:
            if Profile.objects.get(user=request.user.id):
                pass
        except ObjectDoesNotExist:
            return redirect('/configure')

        # User-specific data
        profile = Profile.objects.get(user=request.user.id)
        currency_short, currency_symbol = Profile.ProfileCurrency(profile)
        
        # Pulls details of the active entry
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

        return render(request, "edit.html", context)
        
        
    @login_required 
    def eraser(request, pk):
        """Delete an existing transaction entry."""
        
        # Prevents the user from skipping the initial configuration step.
        try:
            if Profile.objects.get(user=request.user.id):
                pass
        except ObjectDoesNotExist:
            return redirect('/configure')

        entry = Transaction.objects.get(id=pk)
        if request.method == "POST":
            entry.delete()
            return redirect('/')

        context = {"id": pk}

        return render(request, "delete.html", context)


def categories_view(request):
    """
    Loads the corresponding categories for each type 
    of transaction in the create entry window.
    """
    type_id = request.GET.get('type_id')
    categories = Category.objects.filter(type_id=type_id).all()

    return render(request, 'categories.html', {'categories': categories})