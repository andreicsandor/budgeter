from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect

from authenticator.models import Profile
from budgeter.models import Category, Type
from wallet.models import Transaction


# Retrieves & groups the common and user-specific data

@login_required
def finder(request):
    """Returns the corresponding entries for the applied search & filter criteria."""

    # Unfiltered user-specific entries
    qs = get_entries(request)

    query_type = request.GET.get('input-type')
    query_category_search = request.GET.get('input-category-search')
    query_category = request.GET.get('input-category')
    query_type_advanced = request.GET.get('input-type-advanced')
    query_category_advanced = request.GET.get('input-category-advanced')
    query_date = request.GET.get('input-date')
    query_search = request.GET.get('input-search')

    # Checks the corresponding match for the type filter
    if query_type is not None:
        qs = filter_type(qs, query_type)
    # Checks the corresponding match for the category search input
    if query_category_search is not None:
        qs = search_category(qs, query_category_search)
    # Checks the corresponding match for the category filter
    if query_category is not None:
        qs = filter_category(qs, query_category)
    # Checks the corresponding match for the advanced filter
    if query_type_advanced is None or query_type_advanced == "All":
        if query_category_advanced is None or query_category_advanced == "All":
            if query_date is not None:
                qs = filter_date(qs, query_date)
        else:
            if query_date is not None:
                qs_category = filter_category_advanced(qs, query_category_advanced)
                qs_date = qs = filter_date(qs, query_date)
                qs = qs_category & qs_date
    else:
        if query_category_advanced is None or query_category_advanced == "All":
            if query_date is not None:
                qs_type = filter_type_advanced(qs, query_type_advanced)
                qs_date = filter_date(qs, query_date)
                qs = qs_type & qs_date
        else:
            if query_date is not None:
                qs_type = filter_type_advanced(qs, query_type_advanced)
                qs_category = filter_category_advanced(qs, query_category_advanced)
                qs_date = filter_date(qs, query_date)
                qs = qs_type & qs_category & qs_date
    
    # Checks the corresponding match for the search input
    if query_search is not None:
        qs = search_all(qs, query_search)
        
    return qs


@login_required
def get_entries(request):
    """Retrieves the user's set of entries."""
    user = User.objects.get(pk=request.user.id)
    data = Transaction.objects.filter(user=user).order_by('-date', '-amount', 'name')
    return data


def group_entries(data):
    """Groups the entries into expenses & income."""
    expenses = data.filter(type="1").order_by('-amount')
    income = data.filter(type="2").order_by('-amount')
    return expenses, income


# Searches & filters the user's data

def filter_type(qs, query_type):
    """Filters the entries based on the type criteria."""
    qs = qs.filter(type__name__iexact=query_type)
    return qs


def filter_category(qs, query_category):
    """Filters the entries based on the category criteria."""
    qs = qs.filter(category__name__iexact=query_category)
    return qs


def search_category(qs, query_category_search):
    """Filters the entries based on the category search query."""
    qs = qs.filter(category__name__icontains=query_category_search)
    return qs


def filter_type_advanced(qs, query_type_advanced):
    """Filters the entries based on the advanced type criteria."""
    qs = qs.filter(type__name__iexact=query_type_advanced)
    return qs


def filter_category_advanced(qs, query_category_advanced):
    """Filters the entries based on the advanced category criteria."""
    qs = qs.filter(category__name__iexact=query_category_advanced)
    return qs


def filter_date(qs, query_date):
    """Filters the entries based on the date range."""
    start_date, end_date = format_date(query_date)
    qs = qs.filter(date__range=[start_date, end_date])
    return qs


def search_all(qs, query_search):
    """Filters the entries based on the search query."""
    if check_type(query_search):
        qs = qs.filter(type__name__icontains=query_search)
    elif check_category(query_search):
        qs = qs.filter(category__name__icontains=query_search)
    elif check_note(query_search):
        qs = qs.filter(note__icontains=query_search)
    else:
        qs = qs.filter(name__icontains=query_search)
    return qs


# Validates & checks if the search query parameters are valid

def check_type(param):
    """Validates the query parameters for entry types."""
    types = list(dict.fromkeys([item.name for item in Type.objects.all()]))
    return param.title() in types


def check_category(param):
    """Validates the query parameters for entry categories."""
    categories = list(dict.fromkeys([item.name for item in Category.objects.all()]))
    return param.title() in categories


def check_note(param):
    """Validates the query parameters for entry notes."""
    notes = list(dict.fromkeys([item.note for item in Transaction.objects.all()]))
    text = []
    for note in notes:
        text.extend(note.lower().split())
    return param.lower() in text


def format_date(date):
    """Formats the date into the proper format"""
    # Splits the input into two dates
    elements = date.split(" - ")
    # Formats the start date
    elements[0] = elements[0].split("/")
    start_date = f"{elements[0][2]}-{elements[0][0]}-{elements[0][1]}"
    # Formats the end date
    elements[1] = elements[1].split("/")
    end_date = f"{elements[1][2]}-{elements[1][0]}-{elements[1][1]}"
    return start_date, end_date


# User & profile configuration tool

def check_configuration(request):
    """Prevents the user from skipping the initial configuration step."""
    try:
        if Profile.objects.get(user=request.user.id):
            pass
    except ObjectDoesNotExist:
        return redirect('/configure')