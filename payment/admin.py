from django.contrib import admin
from .models import Order, ProductConfig


@admin.register(ProductConfig)
class ProductConfigAdmin(admin.ModelAdmin):
    """
    Singleton config — admin can set product name, full price, and deposit price.
    The 'Add' button is hidden once a config exists.
    """
    fields = ["name", "description", "full_price", "deposit_price"]

    def has_add_permission(self, request):
        # Only allow adding if no config exists yet
        return not ProductConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False  # Prevent accidental deletion


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "full_name",
        "email",
        "phone",
        "payment_type",
        "amount",
        "payment_status",
        "created_at",
    ]
    list_filter = ["payment_type", "payment_status", "created_at"]
    search_fields = ["full_name", "email", "phone", "stripe_session_id"]
    readonly_fields = [
        "full_name",
        "email",
        "phone",
        "payment_type",
        "amount",
        "stripe_session_id",
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            "Customer Details",
            {"fields": ("full_name", "email", "phone")},
        ),
        (
            "Payment Info",
            {"fields": ("payment_type", "amount", "payment_status")},
        ),
        (
            "Stripe & Timestamps",
            {"fields": ("stripe_session_id", "created_at", "updated_at")},
        ),
    )

    # Allow admin to manually correct payment_status if needed
    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:  # Editing existing order
            # payment_status remains editable so admin can fix edge cases
            pass
        return readonly

    def has_add_permission(self, request):
        return False  # Orders are only created via API