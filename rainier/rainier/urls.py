"""rainier URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from authenticator import views as authentication_views
from wallet import views as transactions_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup', authentication_views.signup_view, name='signup'),
    path('configure', authentication_views.configure_view, name='configure'),
    path('login', authentication_views.login_view, name='login'),
    path('logout', authentication_views.logout_view, name='logout'),
    path('account', authentication_views.account_view, name='account'),
    path('preferences', authentication_views.preferences_view, name='preferences'),
    path('', transactions_views.home_view, name='home'),
    path('create', transactions_views.create_view, name='create'),
    path('edit/<str:pk>', transactions_views.edit_view, name='edit'),
    path('delete/<str:pk>', transactions_views.delete_view, name='delete'),
    path('ajax/categories/', transactions_views.categories_view, name='ajax_categories'),
]