from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("me/", views.me, name="me"),
    path("profile/", views.update_profile, name="update-profile"),
    path("plans/", views.plan_prices, name="plan-prices"),
    path("payment/", views.process_payment, name="process-payment"),
    path("payments/", views.my_payments, name="my-payments"),
]