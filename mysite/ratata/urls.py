from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("home/", views.home, name="home"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("accounts/", views.accounts, name="accounts"),
    path("accounts/<int:account_id>/", views.account, name="account"),
]
