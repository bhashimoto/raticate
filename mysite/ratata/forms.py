from django import forms


class AccountForm(forms.Form):
    account_name = forms.CharField(label="Account name", max_length=200)

class LoginForm(forms.Form):
    username = forms.CharField(label="username", max_length=200)
    password = forms.CharField(widget=forms.PasswordInput())
