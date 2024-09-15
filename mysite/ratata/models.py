from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Account(models.Model):
    name = models.CharField(max_length=200)
    #users = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name.__str__()

class AccountUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

class Transaction(models.Model):
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    account = models.ForeignKey(Account,default=1,  on_delete=models.CASCADE)
    amount = models.DecimalField(blank=False, default=0.0, decimal_places=2, max_digits=12)
    paid_by = models.ForeignKey(User, default=1, on_delete=models.CASCADE)


class Debt(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="debts")
    who_owes = models.ForeignKey(User, default=1, on_delete=models.CASCADE, related_name="who_owes")
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    amount = models.DecimalField(blank=False, default=0.0, decimal_places=2, max_digits=12)

class AccountInvitation(models.Model):
    INVITATION_STATUS = [
        ("N", "New"),
        ("A", "Accepted"),
        ("R", "Rejected"),
    ]
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, default=1, related_name="from_user", on_delete=models.CASCADE)
    account = models.ForeignKey(Account, default=1, on_delete=models.CASCADE)
    status= models.CharField(max_length=1, choices=INVITATION_STATUS, default="N")

class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pix_key = models.TextField(max_length=200, blank=True)
    name = models.TextField(max_length=200, blank=True)