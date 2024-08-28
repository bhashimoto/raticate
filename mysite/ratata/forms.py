from django import forms


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
