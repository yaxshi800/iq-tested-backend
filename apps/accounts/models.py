from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta


class Profile(models.Model):
    PLAN_CHOICES = [
        ("free", "Free"),
        ("pro", "Pro"),
        ("ultimate", "Ultimate"),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    full_name = models.CharField(max_length=200, blank=True)
    passport_series = models.CharField(max_length=20, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default="free")
    plan_started_at = models.DateTimeField(null=True, blank=True)
    plan_expires_at = models.DateTimeField(null=True, blank=True)

    certificate_issued = models.BooleanField(default=False)
    certificate_uuid = models.UUIDField(null=True, blank=True, unique=True)
    certificate_downloads = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} — {self.plan}"

    @property
    def is_certificate_ready(self):
        return bool(self.full_name and self.passport_series and self.phone_number)

    @property
    def is_pro(self):
        return self.plan in ("pro", "ultimate") and self._plan_active()

    @property
    def is_ultimate(self):
        return self.plan == "ultimate" and self._plan_active()

    @property
    def is_free(self):
        return self.plan == "free" or not self._plan_active()

    def _plan_active(self):
        if not self.plan_expires_at:
            return False
        return self.plan_expires_at > timezone.now()

    def activate_plan(self, plan_name, days=30):
        self.plan = plan_name
        self.plan_started_at = timezone.now()
        self.plan_expires_at = timezone.now() + timedelta(days=days)
        self.save()


class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]
    CARD_TYPE_CHOICES = [
        ("uzcard", "Uzcard"),
        ("humo", "Humo"),
        ("visa", "Visa"),
        ("mastercard", "Mastercard"),
        ("amex", "American Express"),
        ("unknown", "Unknown"),
    ]
    PLAN_CHOICES = [
        ("pro", "Pro"),
        ("ultimate", "Ultimate"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="payments"
    )
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="UZS")

    card_type = models.CharField(
        max_length=20, choices=CARD_TYPE_CHOICES, default="unknown"
    )
    card_last4 = models.CharField(max_length=4, blank=True)
    card_holder = models.CharField(max_length=100, blank=True)

    transaction_id = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    admin_account = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} — {self.plan} — {self.amount} — {self.status}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)