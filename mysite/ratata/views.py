from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .forms import AccountForm, LoginForm, SignupForm
from .models import Account

# Create your views here.
def index(request):
    return render(request, "ratata/index.html")


def user_signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            User.objects.create_user(username=username, email=email, password=password)
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user, backend=None)
                return redirect("home")
    else:
        form = SignupForm
        return render(request, "ratata/signup.html", {"signup_form": form})


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user, backend=None)
                return redirect("home")
    else:
        form = LoginForm
        return render(request, "ratata/login.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect("/ratata/")


@login_required
def home(request):
    # TODO: get user accounts
    accounts = Account.objects.filter(users=request.user)
    account_create_form = AccountForm
    return render(request, "ratata/home.html", {"account_create_form": account_create_form, "accounts":accounts})


@login_required
def account(request, account_id):
    account = get_object_or_404(Account, pk=account_id)
    return render(request, "ratata/account.html", {"account": account})


@login_required
def accounts(request):
    if request.method == "POST":
        form = AccountForm(request.POST)
        if form.is_valid():
            account = Account(name=form.cleaned_data["account_name"])
            account.save()
            account.users.add(request.user)
            account.save()

            response = HttpResponse()
            response.headers["HX-Trigger"] = "newAccount"
            return response
    else:
        accounts = Account.objects.filter(users=request.user)
        return render(request, "ratata/components/accounts_list.html", {"accounts": accounts})

