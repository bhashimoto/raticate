import base64
from io import BytesIO
import logging
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

import qrcode
from crc import Calculator, Crc16

from .forms import AccountForm, AccountMemberForm, LoginForm, SignupForm, TransactionForm
from .models import Account, Transaction, Debt, AccountInvitation, AccountUser
logger = logging.getLogger(__name__)
# Create your views here.

def index(request):
    if request.user.is_authenticated:
        return redirect("home")
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
    error = None
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user, backend=None)
                return redirect("home")
        error = "login failed"
    form = LoginForm
    return render(request, "ratata/login.html", {"form": form, "error": error})


def user_logout(request):
    logout(request)
    return redirect("index")


@login_required
def home(request):
    # TODO: get user accounts
    accounts = AccountUser.objects.filter(user=request.user)
    account_create_form = AccountForm
    invitations = AccountInvitation.objects.filter(user=request.user, status="N")
    return render(request, "ratata/home.html", {
        "account_create_form": account_create_form, 
        "accounts":accounts,
        "invitations": invitations,
        })


@login_required
def account(request, account_id):
    account = get_object_or_404(Account, pk=account_id)
    members = AccountUser.objects.filter(account=account)
    transactions = Transaction.objects.filter(account=account)
    transaction_form = TransactionForm(account=account)
    members_form = AccountMemberForm()
    payments = calculate_payments(account=account)
    pending_invites = AccountInvitation.objects.filter(account=account, status="N")

    image = generate_pix_qr("13668474745", payments[0]["amount"], "Bruno Hashimoto", "Rio de Janeiro")
    return render(request, "ratata/account.html", {
        "account": account, 
        "members": members,
        "transactions":transactions , 
        "transaction_create_form": transaction_form,
        "account_members_create_form": members_form,
        "payments": payments,
        "invitations": pending_invites,
        "pix": image.decode()
    })

def generate_pix_qr(key, amount, name, city):
    merchant_account_info = "0014br.gov.bcb.pix" + f"01{add_length(key)}"
    amount_string = f"{amount:.2f}"
    pre_crc = f"00020126" + add_length(merchant_account_info) + "52040000530398654" + add_length(amount_string) + "5802BR59" + add_length(name) +"60" + add_length(city) + "6304"
    
    calculator = Calculator(Crc16.IBM_3740)
    cs = calculator.checksum(pre_crc.encode())

    code = pre_crc + hex(cs).encode().decode()[2:].upper()
    img = qrcode.make(code)
    buffered = BytesIO()
    img.save(buffered)
    img_string = base64.b64encode(buffered.getvalue())
    
    return img_string


def add_length(string):
    return f"{len(string):02d}{string}"


@login_required
def accounts(request):
    if request.method == "POST":
        form = AccountForm(request.POST)
        if form.is_valid():
            account = Account(name=form.cleaned_data["account_name"])
            account.save()
            AccountUser.objects.create(user=request.user,account=account)

            account_create_form = AccountForm()
            response = render(request, "ratata/components/account_create_form.html", {"account_create_form": account_create_form})
            response.headers["HX-Trigger"] = "newAccount"
            return response
    else:
        accounts = AccountUser.objects.filter(user=request.user)
        return render(request, "ratata/components/accounts_list.html", {"accounts": accounts})

@login_required
def transaction_form(request, account_id):
    try:
        account = Account.objects.get(pk=account_id)
        form = TransactionForm(account=account)
        return render(request, "ratata/components/transaction_create_form.html", {"account": account, "transaction_create_form": form, "error": err})
    except:
        return HttpResponse("error loading form")


@login_required
def transactions(request, account_id):
    if request.method == "POST":
        try:
            account = Account.objects.get(pk=account_id)
            form = TransactionForm(request.POST, account=account)
            if form.is_valid():
                description = form.cleaned_data["description"]
                amount = form.cleaned_data["amount"]
                members = form.cleaned_data["members"]
                paid_by = form.cleaned_data["paid_by"]
                transaction = Transaction.objects.create(description=description, 
                                                         amount=amount, 
                                                         account=account,
                                                         paid_by=paid_by)

                create_debts(members=members, transaction=transaction, amount=amount)

                form = TransactionForm(account=account)
                response = render(request, "ratata/components/transaction_create_form.html", {"account": account, "transaction_create_form": form})
                response.headers["HX-Trigger"] = "newTransaction"
                return response
            else:
                form = TransactionForm(account=account)
                err = "invalid form data. please verify inputs"
                return render(request, "ratata/components/transaction_create_form.html", {"account": account, "transaction_create_form": form, "error": err})
        except Exception as ex:
            logger.info("raised exception", ex)
            return HttpResponse(ex)
    else:
        transactions = Transaction.objects.filter(account = Account.objects.get(pk=account_id))
        return render(request, "ratata/components/transactions_list.html", {"transactions": transactions})

def create_debts(members, transaction, amount):
    num_members = len(members)
    value_cents = amount*100
    rest = (value_cents % num_members)/100
    debt = None
    for member in members:
        debt = Debt.objects.create(transaction=transaction, who_owes=member, amount=(value_cents//num_members)/100)
    if rest:
        debt.amount += rest
        debt.save()
        
@login_required
def payments(request, account_id):
    account = Account.objects.get(pk=account_id)
    payments = calculate_payments(account=account)
    return render(request, "ratata/components/account_payment_summary.html", {"payments":payments})

def calculate_payments(account):
    # 0 or 1 users, nothing to do
    users = AccountUser.objects.filter(account=account)
    if len(users)< 2:
        return []

    debts = Debt.objects.filter(transaction__in = Transaction.objects.filter(account=account))
    debts_summary = {}
    for debt in debts:
        if debt.who_owes not in debts_summary:
            debts_summary[debt.who_owes] = {"owes": 0, "is_owed": 0}
        if debt.transaction.paid_by not in debts_summary:
            debts_summary[debt.transaction.paid_by] = {"owes": 0, "is_owed": 0}
        debts_summary[debt.who_owes]["owes"] += debt.amount
        debts_summary[debt.transaction.paid_by]["is_owed"] += debt.amount
    
    # only one user in account, there is no calculation to be made
    if len(debts_summary) < 2:
        return []

    tally = []
    for user in debts_summary:
        balance = debts_summary[user]["is_owed"] - debts_summary[user]["owes"]
        tally.append([user, balance])

    tally = sorted(tally, key=lambda x: x[1], reverse=True)
    
    pay_from = len(tally) - 1
    pay_to  = 0
    payments = []

    while True:
        if tally[pay_to][1] == 0.0:
            break
        if pay_from == pay_to:
            break
        if tally[pay_from][1] == 0.0:
            break
        if tally[pay_to][1] > tally[pay_from][1]:
            payments.append({
                "from": tally[pay_from][0],
                "to": tally[pay_to][0],
                "amount": abs(tally[pay_from][1]),
                })
            tally[pay_to][1] -= tally[pay_from][1]
            tally[pay_from][1] = 0
            pay_from -= 1
        elif tally[pay_to][1] == tally[pay_from][1]:
            payments.append({
                "from": tally[pay_from][0],
                "to": tally[pay_to][0],
                "amount": abs(tally[pay_from][1]),
                })
            tally[pay_from][1] = 0
            tally[pay_to][1] = 0
            pay_to += 1
            pay_from -= 1
        else:
            payments.append({
                "from": tally[pay_from][0],
                "to": tally[pay_to][0],
                "amount": abs(tally[pay_to][1]),
                })
            tally[pay_from][1] -= tally[pay_to][1]
            tally[pay_to][1] = 0
            pay_to += 1

    return payments



@login_required
def members(request, account_id):
    if request.method == "POST":
        try:
            form = AccountMemberForm(request.POST)
            if form.is_valid():
                account = Account.objects.get(pk=account_id)
                username = form.cleaned_data["member"]
                try:
                    user = User.objects.get(username=username)
                    matches = AccountInvitation.objects.filter(user=user, account=account)
                    if not matches:
                        AccountInvitation.objects.create(user=user, account=account)
                    form = AccountMemberForm()
                    response = render(request, "ratata/components/account_members_create_form.html", {
                        "account":account,
                        "account_members_create_form": form,
                        })
                    response.headers["HX-Trigger"] = "newMember"
                    return response
                except:
                    error = "user not found"
                    form = AccountMemberForm()
                    return render(request, "ratata/components/account_members_create_form.html", {
                        "account":account,
                        "account_members_create_form": form,
                        "error": error
                        })
        except:
            return HttpResponse("error")
    else:
        try:
            account = Account.objects.get(pk=account_id)
            members = AccountUser.objects.filter(account=account, active=True)
            return render(request, "ratata/components/account_members_list.html", {"account":account, "members":members})
        except:
            return HttpResponse("error")

@login_required
def members_form(request, account_id):
    account = Account.objects.get(pk=account_id)
    form = AccountMemberForm(account=account)
    return render(request, "ratata/components/account_members_create_form.html", {"account": account, "account_members_create_form": form})

@login_required
def invitation_accept(request, invitation_id):
    if request.method == "POST":
        try:
            invite = AccountInvitation.objects.get(pk=invitation_id)
            logger.info(f"invite id: {invite.id}")
            invite.status = "A"
            invite.save()
            account = Account.objects.get(pk=invite.account.id)
            AccountUser.objects.create(user=invite.user, account=account)
            return return_trigger("invitationUpdate")
        except:
            return render(request, "ratata/components/account_invitation_list.html", {"invitation": invite})
    else:
        invite = AccountInvitation.objects.get(pk=invitation_id)
        return render(request, "ratata/components/account_invitation_list.html", {"invitation": invite})

@login_required
def invitation(request):
    invites = AccountInvitation.objects.filter(user=request.user, status="N")
    return render(request, "ratata/components/account_invitation_list.html", {"invitation": invites})

@login_required
def pending_invitations(request, account_id):
    account = Account.objects.get(pk=account_id)
    invitations = AccountInvitation.objects.filter(account=account, status="N")
    return render(request, "ratata/components/pending_invitations.html", {"account":account, "invitations":invitations})


def return_trigger(trigger:str) -> HttpResponse:
    response = HttpResponse()
    response.headers['HX-Trigger'] = trigger
    return response
