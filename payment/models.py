from django.db import models

# --- Product Price Configuration --------------------------------------------
class ProductConfig(models.Model):
    """
    Singleton model. Admin sets the product name, full price, and deposit price.
    Only one row should ever exist (enforced via save override).
    """
    name = models.CharField(max_length=255, default="Product")
    description = models.TextField(blank=True)
    full_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Full payment amount in USD")
    deposit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Deposit/partial payment amount in USD")

    class Meta:
        verbose_name = "Product Configuration"
        verbose_name_plural = "Product Configuration"

    def save(self, *args, **kwargs):
        self.pk = 1  # Enforce singleton
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # Prevent deletion

    def __str__(self):
        return f"{self.name} | Full: ${self.full_price} | Deposit: ${self.deposit_price}"

# --- Customer Orders ------------------------------------------------------
class Order(models.Model):
    PAYMENT_TYPE_FULL = "full"
    PAYMENT_TYPE_DEPOSIT = "deposit"
    PAYMENT_TYPE_CHOICES = [
        (PAYMENT_TYPE_FULL, "Full Payment"),
        (PAYMENT_TYPE_DEPOSIT, "Deposit Payment"),
    ]

    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
        (STATUS_FAILED, "Failed"),
    ]

    # User details
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)

    # Payment info
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount charged for this order")
    payment_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)

    # Stripe tracking
    stripe_session_id = models.CharField(max_length=255, blank=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} | {self.get_payment_type_display()} | {self.get_payment_status_display()} | ${self.amount}"