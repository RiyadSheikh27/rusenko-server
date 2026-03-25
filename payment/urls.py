from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import (
    CreateOrderView,
    PaymentCancelView,
    PaymentSuccessView,
    ProductConfigView,
    StripeWebhookView,
)

urlpatterns = [
    # API endpoints
    path("product/", ProductConfigView.as_view(), name="product-config"),
    path("order/", CreateOrderView.as_view(), name="create-order"),

    # Stripe webhook — must be csrf_exempt
    path("webhook/", csrf_exempt(StripeWebhookView.as_view()), name="stripe-webhook"),

    # Stripe redirect pages
    path("payment/success/", PaymentSuccessView.as_view(), name="payment-success"),
    path("payment/cancel/", PaymentCancelView.as_view(), name="payment-cancel"),
]