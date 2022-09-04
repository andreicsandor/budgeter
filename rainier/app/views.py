import datetime

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .forms import LoginForm
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