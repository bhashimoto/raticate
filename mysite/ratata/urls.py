from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("home/", views.home, name="home"),
    path("signup/", views.user_signup, name="signup"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("accounts/", views.accounts, name="accounts"),
    path("accounts/<int:account_id>/", views.account, name="account"),
    path("accounts/<int:account_id>/transactions", views.transactions, name="transactions"),
    path("accounts/<int:account_id>/transaction_form", views.transaction_form, name="transaction_form"),
    path("accounts/<int:account_id>/payments", views.payments, name="payments"),
    path("accounts/<int:account_id>/payments/<int:user_id>", views.payment, name="payment"),
    path("accounts/<int:account_id>/members", views.members, name="members"),
    path("accounts/<int:account_id>/members_form", views.members_form, name="members_form"),
    path("accounts/<int:account_id>/invitations", views.pending_invitations, name="pending_invitations"),
    path("invitations/<int:invitation_id>", views.invitation_accept, name="invitation_accept"),
    path("invitations", views.invitation, name="invitation"),
]
