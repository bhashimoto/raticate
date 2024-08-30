from django import forms
from django.contrib.auth.models import User


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
    amount = forms.DecimalField(label="amount")
    paid_by = forms.ModelChoiceField(label="paid by", queryset=None)
    members = forms.ModelMultipleChoiceField(label="Split between", queryset=None, widget=forms.CheckboxSelectMultiple())
    def __init__(self, *args, **kwargs):
        account = kwargs.pop('account')
        super().__init__(*args, **kwargs)
        self.fields['members'].queryset = account.users.all()
        self.fields['paid_by'].queryset = account.users.all()

class AccountMemberForm(forms.Form):
    members = forms.ModelMultipleChoiceField(label="users",required=False, queryset=None)
    def __init__(self, *args, **kwargs):
        account = kwargs.pop('account')
        super().__init__(*args,**kwargs)
        current_members = account.users.values_list('pk', flat=True)
        self.fields['members'].queryset = User.objects.exclude(pk__in=current_members)
