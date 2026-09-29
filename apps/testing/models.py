import uuid
from django.db import models


class Question(models.Model):
    CATEGORY_CHOICES = [
        ("pattern", "Pattern Recognition & Matrix"),
        ("spatial", "Spatial Visualization"),
        ("numerical", "Numerical Sequences"),
        ("abstract", "Abstract Reasoning"),
    ]

    question_text = models.TextField()
    explanation = models.TextField(blank=True)
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)

    image_url = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    difficulty = models.FloatField(default=1.0)
    correct_index = models.PositiveSmallIntegerField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"[{self.category}] {self.question_text[:50]}"

    @property
    def options(self):
        return [self.option_a, self.option_b, self.option_c, self.option_d]


class TestSession(models.Model):
    STATUS_CHOICES = [
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("expired", "Expired"),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(
        "auth.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="test_sessions",
    )
    language = models.CharField(max_length=2, default="uz")
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="in_progress"
    )

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)

    raw_score = models.FloatField(default=0.0)
    accuracy = models.FloatField(default=0.0)
    iq_score = models.PositiveSmallIntegerField(null=True, blank=True)
    percentile = models.FloatField(null=True, blank=True)
    category_breakdown = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"Session {self.uuid} ({self.status})"


class UserAnswer(models.Model):
    session = models.ForeignKey(
        TestSession, related_name="answers", on_delete=models.CASCADE
    )
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    selected_index = models.PositiveSmallIntegerField(null=True, blank=True)
    time_spent = models.PositiveIntegerField(default=0)
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ("session", "question")