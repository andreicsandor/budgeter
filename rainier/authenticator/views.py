from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.views import View

from authenticator.forms import LoginForm, ProfileForm, SignUpForm, UserForm
from authenticator.models import Profile

# Create your views here.

@login_required
class Utilities(View):
    """
    Represents a child class for views. 
    
    Displays the account management, preferences and 
    initial settings configuration pages and forms.
    """

    def setup(request):
        """Displays the initial settings configuration page and form."""

        # Prevents the user from visiting the initial configuration again after the setup.
        try:
            if Profile.objects.get(user=request.user.id):
                return redirect('.')
        except ObjectDoesNotExist:
            if request.method == "POST":
                form = ProfileForm(request.POST)
                if form.is_valid():
                    obj = form.save(commit=False)
                    obj.user = User.objects.get(pk=request.user.id)
                    obj.save()
                    return redirect('.')
            else:
                form = ProfileForm()

        context = {"form": form}

        return render(request, "configure.html", context)


    def account(request):
        """Displays the account management page and form."""

        # Prevents the user from skipping the initial configuration step
        try:
            if Profile.objects.get(user=request.user.id):
                pass
        except ObjectDoesNotExist:
            return redirect('/configure')

        user = User.objects.get(pk=request.user.id)
        form = UserForm(instance=user)
        if request.method == "POST":
            form = UserForm(request.POST, instance=user)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.save()
                return redirect('/')

        context = {"form": form}

        return render(request, "account.html", context)


    def preferences(request):
        """Displays the preferences page and form."""

        # Prevents the user from skipping the initial configuration step
        try:
            if Profile.objects.get(user=request.user.id):
                pass
        except ObjectDoesNotExist:
            return redirect('/configure')

        user = User.objects.get(pk=request.user.id)
        profile = Profile.objects.get(user=user)
        form = ProfileForm(instance=profile)
        if request.method == "POST":
            form = ProfileForm(request.POST, instance=profile)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.save()
                return redirect('/account')

        context = {"form": form}

        return render(request, "preferences.html", context)


    def validator(request):
        """Prevents the user from skipping the initial configuration step."""
        try:
            if Profile.objects.get(user=request.user.id):
                pass
        except ObjectDoesNotExist:
            return redirect('/configure')


def signup_view(request):
    """Displays the form and creates a new user account."""

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
            return redirect('/configure')
    else:
        form = SignUpForm()
        
    context = {"form": form}
    
    return render(request, "signup.html", context)


def login_view(request):
    """Displays the form and logs in the user."""

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

    context = {"form": form}

    return render(request, "login.html", context)


def logout_view(request):
    """Displays the form and logs out the user."""
    
    logout(request)
    return redirect('/')