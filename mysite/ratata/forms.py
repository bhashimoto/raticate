from django import forms
from django.contrib.auth.models import User
from .models import AccountUser
from django.db.models import Subquery


class AccountForm(forms.Form):
    account_name = forms.CharField(label="Nome da Conta", max_length=200)

class LoginForm(forms.Form):
    username = forms.CharField(label="usuário", max_length=200)
    password = forms.CharField(widget=forms.PasswordInput())

class SignupForm(forms.Form):
    username = forms.CharField(label="usuário", max_length=200)
    email = forms.EmailField(label="email")
    firstname = forms.CharField(label="firstname")
    lastname= forms.CharField(label="lastname")
    pix = forms.CharField(label="chave pix", max_length=200, required=False)
    password = forms.CharField(label="senha", widget=forms.PasswordInput())

class TransactionForm(forms.Form):
    description = forms.CharField(label="descrição", max_length=200)
    amount = forms.DecimalField(label="valor", decimal_places=2)
    paid_by = forms.ModelChoiceField(label="pago por", queryset=None)
    members = forms.ModelMultipleChoiceField(label="Dividir entre", queryset=None, widget=forms.CheckboxSelectMultiple())
    def __init__(self, *args, **kwargs):
        account = kwargs.pop('account')
        super().__init__(*args, **kwargs)

        users_pk = AccountUser.objects.filter(account=account).values_list('user')
        self.fields['members'].queryset = User.objects.filter(pk__in=users_pk)
        self.fields['paid_by'].queryset = User.objects.filter(pk__in=users_pk)


class AccountMemberForm(forms.Form):
    member = forms.CharField(label="usuário", max_length=150)
