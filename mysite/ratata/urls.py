from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("accounts/", views.accounts, name="accounts"),
    path("accounts/<int:account_id>/", views.account, name="account"),
]
