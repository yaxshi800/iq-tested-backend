import uuid
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


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
    PLAN_CHOICES = [("pro", "Pro"), ("ultimate", "Ultimate")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="UZS")

    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES, default="unknown")
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
        return f"{self.user.username} — {self.plan} — {self.amount}"


# ═══════════════════════════════════════════
# TEACHER / CLASSROOM
# ═══════════════════════════════════════════
class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher_profile")
    school_name = models.CharField(max_length=200, blank=True)
    subject = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Teacher: {self.user.username}"


class Classroom(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="classrooms")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    invite_code = models.CharField(max_length=8, unique=True, db_index=True, blank=True)
    grade = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.invite_code:
            import random
            import string
            self.invite_code = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=6)
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.invite_code})"


class ClassMembership(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="members")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="class_memberships")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("classroom", "student")

    def __str__(self):
        return f"{self.student.username} → {self.classroom.name}"


# ═══════════════════════════════════════════
# ACHIEVEMENTS
# ═══════════════════════════════════════════
class Achievement(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name_uz = models.CharField(max_length=100)
    description_uz = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=30, blank=True, default="amber")
    points = models.PositiveIntegerField(default=10)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name_uz


class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="achievements")
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "achievement")


class DailyStreak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="daily_streak")
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_activity = models.DateField(null=True, blank=True)
    total_points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}: {self.current_streak} kun"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
        DailyStreak.objects.get_or_create(user=instance)