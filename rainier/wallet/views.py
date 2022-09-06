import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views import View

from authenticator.models import Profile
from authenticator.views import Utilities
from budgeter.models import Category, Type
from wallet import services
from wallet.forms import TransactionForm
from wallet.models import Transaction

# Create your views here.

@login_required
class Viewer(View):
    """
    Represents a child class for views. 

    Displays the entries, queries, user-specific statistics and 
    main forms through multiple screens.
    """

    def dashboard(request):
        """Displays the corresponding entries & statistics for the current user."""

        # Prevents the user from skipping the initial configuration step
        Utilities.validator(request)

        # Common data
        types = Type.TypeList(Type)
        categories_expenses, categories_income = Category.CategoryList(Category)

        # User-specific data
        profile = Profile.objects.get(user=request.user.id)
        currency_short, currency_symbol = Profile.ProfileCurrency(profile)
        entries = services.get_entries(request)
        expenses, income = services.group_entries(entries)

        # Filtered entries
        query = Viewer.finder(request)
        
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
        for entry in expenses:
            if Transaction.TransactionMonth(entry) == month_current:
                expenses_current += entry.amount
        for entry in income:
            if Transaction.TransactionMonth(entry) == month_current:
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
        for month in months_previous:
            for entry in expenses:
                if Transaction.TransactionMonth(entry) == month:
                    expenses_previous[month] += entry.amount
        income_previous = dict.fromkeys(months_previous, 0)
        for month in months_previous:
            for entry in income:
                if Transaction.TransactionMonth(entry) == month:
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


    def finder(request):
        """Returns the corresponding entries for the applied search & filter criteria."""

        # Unfiltered user-specific entries
        qs = services.get_entries(request)

        query_type = request.GET.get('input-type')
        query_category_search = request.GET.get('input-category-search')
        query_category = request.GET.get('input-category')
        query_type_advanced = request.GET.get('input-type-advanced')
        query_category_advanced = request.GET.get('input-category-advanced')
        query_date = request.GET.get('input-date')
        query_search = request.GET.get('input-search')

        # Checks the corresponding match for the type filter
        if query_type is not None:
            qs = services.filter_type(qs, query_type)
        # Checks the corresponding match for the category search input
        if query_category_search is not None:
            qs = services.search_category(qs, query_category_search)
        # Checks the corresponding match for the category filter
        if query_category is not None:
            qs = services.filter_category(qs, query_category)
        # Checks the corresponding match for the advanced filter
        if query_type_advanced is None or query_type_advanced == "All":
            if query_category_advanced is None or query_category_advanced == "All":
                if query_date is not None:
                    qs = services.filter_date(qs, query_date)
            else:
                if query_date is not None:
                    qs_category = services.filter_category_advanced(qs, query_category_advanced)
                    qs_date = qs = services.filter_date(qs, query_date)
                    qs = qs_category & qs_date
        else:
            if query_category_advanced is None or query_category_advanced == "All":
                if query_date is not None:
                    qs_type = services.filter_type_advanced(qs, query_type_advanced)
                    qs_date = services.filter_date(qs, query_date)
                    qs = qs_type & qs_date
            else:
                if query_date is not None:
                    qs_type = services.filter_type_advanced(qs, query_type_advanced)
                    qs_category = services.filter_category_advanced(qs, query_category_advanced)
                    qs_date = services.filter_date(qs, query_date)
                    qs = qs_type & qs_category & qs_date
        
        # Checks the corresponding match for the search input
        if query_search is not None:
            qs = services.search_all(qs, query_search)

        return qs


    def creator(request):
        """Creates a new transaction entry."""

        # Prevents the user from skipping the initial configuration step
        Utilities.validator(request)

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


    def editor(request, pk):
        """Edit an existing transaction entry."""

        # Prevents the user from skipping the initial configuration step
        Utilities.validator(request)

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
        
 
    def eraser(request, pk):
        """Delete an existing transaction entry."""
        
        # Prevents the user from skipping the initial configuration step
        Utilities.validator(request)

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