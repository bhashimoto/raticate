from django import forms
from django.contrib.auth.models import User
from .models import AccountUser
from django.db.models import Subquery


class AccountForm(forms.Form):
    account_name = forms.CharField(label="Account name", max_length=200)

class LoginForm(forms.Form):
    username = forms.CharField(label="username", max_length=200)
    password = forms.CharField(widget=forms.PasswordInput())

class SignupForm(forms.Form):
    username = forms.CharField(label="username", max_length=200)
    email = forms.EmailField(label="email")
    password = forms.CharField(label="password", widget=forms.PasswordInput())

class TransactionForm(forms.Form):
    description = forms.CharField(label="description", max_length=200)
    amount = forms.DecimalField(label="amount", decimal_places=2)
    paid_by = forms.ModelChoiceField(label="paid by", queryset=None)
    members = forms.ModelMultipleChoiceField(label="Split between", queryset=None, widget=forms.CheckboxSelectMultiple())
    def __init__(self, *args, **kwargs):
        account = kwargs.pop('account')
        super().__init__(*args, **kwargs)

        users_pk = AccountUser.objects.filter(account=account).values_list('user')
        self.fields['members'].queryset = User.objects.filter(pk__in=users_pk)
        self.fields['paid_by'].queryset = User.objects.filter(pk__in=users_pk)


class AccountMemberForm(forms.Form):
    member = forms.CharField(label="username", max_length=150)
