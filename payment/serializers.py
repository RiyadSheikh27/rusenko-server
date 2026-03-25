from rest_framework import serializers
from .models import Order, ProductConfig

# --- Product Price Configuration --------------------------------------------
class ProductConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductConfig
        fields = ["name", "description", "full_price", "deposit_price"]

# --- Customer Orders ------------------------------------------------------
class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["full_name", "email", "phone", "payment_type"]

    def validate_payment_type(self, value):
        if value not in [Order.PAYMENT_TYPE_FULL, Order.PAYMENT_TYPE_DEPOSIT]:
            raise serializers.ValidationError("payment_type must be 'full' or 'deposit'.")
        return value