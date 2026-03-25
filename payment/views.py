import stripe
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView

from .models import Order, ProductConfig
from .serializers import OrderCreateSerializer, ProductConfigSerializer
from utils.views import APIResponse

stripe.api_key = settings.STRIPE_SECRET_KEY


# --- Product Price Configuration --------------------------------------------
class ProductConfigView(APIView, APIResponse):
    def get(self, request):
        config = ProductConfig.objects.filter(pk=1).first()
        if not config:
            return self.error_response(
                message="Product has not been configured yet.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = ProductConfigSerializer(config)
        return self.success_response(data=serializer.data)


# --- Customer Orders ------------------------------------------------------
class CreateOrderView(APIView, APIResponse):
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return self.error_response(
                errors=serializer.errors,
                message="Invalid order data.",
            )

        config = ProductConfig.objects.filter(pk=1).first()
        if not config:
            return self.error_response(
                message="Product has not been configured yet.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        payment_type = serializer.validated_data["payment_type"]
        amount = config.full_price if payment_type == Order.PAYMENT_TYPE_FULL else config.deposit_price
        label = "Full Payment" if payment_type == Order.PAYMENT_TYPE_FULL else "Deposit Payment"

        order = Order.objects.create(
            full_name=serializer.validated_data["full_name"],
            email=serializer.validated_data["email"],
            phone=serializer.validated_data.get("phone", ""),
            payment_type=payment_type,
            amount=amount,
        )

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "unit_amount": int(amount * 100),
                            "product_data": {
                                "name": config.name,
                                "description": f"{label} — {config.description}" if config.description else label,
                            },
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                customer_email=order.email,
                metadata={"order_id": order.id},
                success_url=settings.STRIPE_SUCCESS_URL + f"?order_id={order.id}",
                cancel_url=settings.STRIPE_CANCEL_URL + f"?order_id={order.id}",
            )
        except stripe.error.StripeError as e:
            order.payment_status = Order.STATUS_FAILED
            order.save(update_fields=["payment_status"])
            return self.error_response(
                errors={"stripe": str(e)},
                message="Failed to create Stripe session.",
                status_code=status.HTTP_502_BAD_GATEWAY,
            )

        order.stripe_session_id = session.id
        order.save(update_fields=["stripe_session_id"])

        return self.success_response(
            data={
                "order_id": order.id,
                "checkout_url": session.url,
                "payment_type": payment_type,
                "amount": str(amount),
            },
            message="Order created. Redirect to checkout_url to complete payment.",
            status_code=status.HTTP_201_CREATED,
        )


# --- Stripe Webhook to handle payment success/failure --------------------------------------------
class StripeWebhookView(APIView, APIResponse):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return self.error_response(
                message="Invalid payload.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except stripe.error.SignatureVerificationError:
            return self.error_response(
                message="Invalid signature.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if event["type"] == "checkout.session.completed":
            self._handle_payment_success(event["data"]["object"])

        elif event["type"] == "checkout.session.expired":
            self._handle_payment_expired(event["data"]["object"])

        return self.success_response(message="Webhook received.")

    def _handle_payment_success(self, session):
        order = Order.objects.filter(stripe_session_id=session["id"]).first()
        if order:
            order.payment_status = Order.STATUS_PAID
            order.save(update_fields=["payment_status", "updated_at"])

    def _handle_payment_expired(self, session):
        order = Order.objects.filter(stripe_session_id=session["id"]).first()
        if order and order.payment_status == Order.STATUS_PENDING:
            order.payment_status = Order.STATUS_FAILED
            order.save(update_fields=["payment_status", "updated_at"])


# --- Success/Cancel Views for redirect after payment --------------------------------------------
class PaymentSuccessView(APIView, APIResponse):
    def get(self, request):
        order_id = request.GET.get("order_id", "")
        return self.success_response(
            data={"order_id": order_id},
            message="Payment completed successfully.",
        )

# --- Success/Cancel Views for redirect after payment --------------------------------------------
class PaymentCancelView(APIView, APIResponse):
    def get(self, request):
        order_id = request.GET.get("order_id", "")
        return self.error_response(
            errors={"order_id": order_id},
            message="Payment was cancelled.",
            status_code=status.HTTP_200_OK,
        )