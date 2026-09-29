from django.contrib import admin
from django.utils.html import format_html
from .models import Profile, Payment


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "plan", "plan_expires_at", "certificate_issued")
    list_filter = ("plan", "certificate_issued")
    search_fields = ("user__username", "full_name", "phone_number")
    readonly_fields = ("certificate_uuid", "created_at", "updated_at")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_id", "user", "plan", "amount_display",
        "card_type", "card_last4", "status_badge", "created_at",
    )
    list_filter = ("plan", "card_type", "status", "currency")
    search_fields = ("user__username", "transaction_id", "card_last4")
    readonly_fields = (
        "user", "plan", "amount", "currency",
        "card_type", "card_last4", "card_holder",
        "transaction_id", "admin_account", "created_at", "completed_at",
    )
    ordering = ("-created_at",)

    def amount_display(self, obj):
        return f"{obj.amount:,.0f} {obj.currency}".replace(",", " ")
    amount_display.short_description = "Summa"

    def status_badge(self, obj):
        colors = {
            "success": "#10b981", "pending": "#f59e0b",
            "failed": "#ef4444", "refunded": "#6b7280",
        }
        color = colors.get(obj.status, "#6b7280")
        return format_html(
            '<span style="background:{};color:white;padding:3px 8px;border-radius:4px;font-size:11px;">{}</span>',
            color, obj.status.upper(),
        )
    status_badge.short_description = "Holat"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.site_header = "CogniTest Admin"
admin.site.site_title = "CogniTest"
admin.site.index_title = "Boshqaruv paneli"