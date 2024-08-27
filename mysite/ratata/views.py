from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .forms import AccountForm
from .models import Account

# Create your views here.
def index(request):
    accounts = Account.objects.all()
    form = AccountForm
    return render(request, "ratata/index.html", {"accounts": accounts, "form": form})

def account(request, account_id):
    account = get_object_or_404(Account, pk=account_id)
    return render(request, "ratata/account.html", {"account": account})

def accounts(request):
    if request.method == "POST":
        
        form = AccountForm(request.POST)
        if form.is_valid():
            account = Account(name=form.cleaned_data["account_nlist_ame"])
            account.save()

            response = HttpResponse()
            response.headers["HX-Trigger"] = "newAccount"
            return response
    else:
        accounts = Account.objects.all()
        return render(request, "ratata/components/accounts_list.html", {"accounts": accounts})
