from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.db.models import Sum, Count
from .models import Profile, Payment


# ═══════════════════════════════════════════
# PROFILE INLINE
# ═══════════════════════════════════════════
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name = "Profil"
    verbose_name_plural = "Profil"
    fields = (
        "full_name",
        "passport_series",
        "phone_number",
        "plan",
        "plan_started_at",
        "plan_expires_at",
        "certificate_issued",
        "certificate_uuid",
        "certificate_downloads",
    )
    readonly_fields = ("certificate_uuid",)


# ═══════════════════════════════════════════
# USER ADMIN (kengaytirilgan)
# ═══════════════════════════════════════════
class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = (
        "username",
        "email",
        "get_plan_badge",
        "get_full_name",
        "is_staff",
        "is_active",
        "date_joined",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "profile__plan",
    )
    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "profile__full_name",
        "profile__phone_number",
        "profile__passport_series",
    )
    ordering = ("-date_joined",)

    def get_plan_badge(self, obj):
        try:
            plan = obj.profile.plan
        except Profile.DoesNotExist:
            plan = "free"

        colors = {
            "free": "#64748b",
            "pro": "#6366f1",
            "ultimate": "#f59e0b",
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            colors.get(plan, "#64748b"),
            plan.upper(),
        )

    get_plan_badge.short_description = "Tarif"

    def get_full_name(self, obj):
        try:
            return obj.profile.full_name or "—"
        except Profile.DoesNotExist:
            return "—"

    get_full_name.short_description = "F.I.SH"


# User'ni qayta ro'yxatdan o'tkazish
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# ═══════════════════════════════════════════
# PROFILE ADMIN
# ═══════════════════════════════════════════
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "full_name",
        "phone_number",
        "plan_badge",
        "plan_expires_at",
        "certificate_issued",
        "created_at",
    )
    list_filter = ("plan", "certificate_issued")
    search_fields = (
        "user__username",
        "user__email",
        "full_name",
        "phone_number",
        "passport_series",
    )
    readonly_fields = (
        "certificate_uuid",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)

    fieldsets = (
        ("Foydalanuvchi", {
            "fields": ("user",)
        }),
        ("Shaxsiy ma'lumotlar", {
            "fields": ("full_name", "passport_series", "phone_number")
        }),
        ("Tarif", {
            "fields": ("plan", "plan_started_at", "plan_expires_at")
        }),
        ("Sertifikat", {
            "fields": (
                "certificate_issued",
                "certificate_uuid",
                "certificate_downloads",
            )
        }),
        ("Sanalar", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def plan_badge(self, obj):
        colors = {
            "free": "#64748b",
            "pro": "#6366f1",
            "ultimate": "#f59e0b",
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            colors.get(obj.plan, "#64748b"),
            obj.plan.upper(),
        )

    plan_badge.short_description = "Tarif"

    # Bulk actions
    actions = ["make_pro", "make_ultimate", "make_free"]

    def make_pro(self, request, queryset):
        for profile in queryset:
            profile.activate_plan("pro", days=30)
        self.message_user(request, f"{queryset.count()} ta foydalanuvchi PRO tarifga o‘tkazildi.")

    make_pro.short_description = "→ PRO tarifga o‘tkazish (30 kun)"

    def make_ultimate(self, request, queryset):
        for profile in queryset:
            profile.activate_plan("ultimate", days=90)
        self.message_user(request, f"{queryset.count()} ta foydalanuvchi ULTIMATE tarifga o‘tkazildi.")

    make_ultimate.short_description = "→ ULTIMATE tarifga o‘tkazish (90 kun)"

    def make_free(self, request, queryset):
        queryset.update(plan="free", plan_expires_at=None)
        self.message_user(request, f"{queryset.count()} ta foydalanuvchi FREE tarifga o‘tkazildi.")

    make_free.short_description = "→ FREE tarifga o‘tkazish"


# ═══════════════════════════════════════════
# PAYMENT ADMIN
# ═══════════════════════════════════════════
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_id_short",
        "user_link",
        "plan_badge",
        "amount_display",
        "card_display",
        "status_badge",
        "created_at",
    )
    list_filter = ("plan", "card_type", "status", "currency", "created_at")
    search_fields = (
        "user__username",
        "user__email",
        "transaction_id",
        "card_last4",
        "card_holder",
    )
    readonly_fields = (
        "user",
        "plan",
        "amount",
        "currency",
        "card_type",
        "card_last4",
        "card_holder",
        "transaction_id",
        "admin_account",
        "created_at",
        "completed_at",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    fieldsets = (
        ("Tranzaksiya", {
            "fields": ("transaction_id", "status", "created_at", "completed_at")
        }),
        ("Foydalanuvchi", {
            "fields": ("user", "plan", "amount", "currency")
        }),
        ("Karta", {
            "fields": ("card_type", "card_last4", "card_holder")
        }),
        ("Admin hisobi", {
            "fields": ("admin_account",),
            "classes": ("collapse",)
        }),
    )

    def transaction_id_short(self, obj):
        return format_html(
            '<span style="font-family:monospace;font-size:11px;">{}…</span>',
            obj.transaction_id[:12],
        )

    transaction_id_short.short_description = "Tranzaksiya ID"

    def user_link(self, obj):
        return format_html(
            '<a href="/admin/auth/user/{}/change/" style="color:#6366f1;font-weight:600;">{}</a>',
            obj.user.id,
            obj.user.username,
        )

    user_link.short_description = "Foydalanuvchi"

    def plan_badge(self, obj):
        colors = {"pro": "#6366f1", "ultimate": "#f59e0b"}
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            colors.get(obj.plan, "#64748b"),
            obj.plan.upper(),
        )

    plan_badge.short_description = "Tarif"

    def amount_display(self, obj):
        return format_html(
            '<span style="font-weight:700;color:#10b981;">{} {}</span>',
            f"{int(obj.amount):,}".replace(",", " "),
            obj.currency,
        )

    amount_display.short_description = "Summa"

    def card_display(self, obj):
        icons = {
            "uzcard": "🟢",
            "humo": "🔵",
            "visa": "🔷",
            "mastercard": "🟠",
            "amex": "🔶",
        }
        icon = icons.get(obj.card_type, "💳")
        return format_html(
            '{} <span style="font-family:monospace;">•••• {}</span>',
            icon,
            obj.card_last4,
        )

    card_display.short_description = "Karta"

    def status_badge(self, obj):
        colors = {
            "success": "#10b981",
            "pending": "#f59e0b",
            "failed": "#ef4444",
            "refunded": "#6b7280",
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            colors.get(obj.status, "#6b7280"),
            obj.status.upper(),
        )

    status_badge.short_description = "Holat"

    # Faqat ko'rish rejimi (xavfsizlik)
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# ═══════════════════════════════════════════
# ADMIN SAYT SOZLAMALARI
# ═══════════════════════════════════════════
admin.site.site_header = "CogniTest Boshqaruv Paneli"
admin.site.site_title = "CogniTest Admin"
admin.site.index_title = "Xush kelibsiz! 👋"