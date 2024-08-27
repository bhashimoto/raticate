from django import forms


class AccountForm(forms.Form):
    account_name = forms.CharField(label="Account name", max_length=200)
