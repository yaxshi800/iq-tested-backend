import uuid
from django.db import models


class TestCategory(models.Model):
    CATEGORY_CHOICES = [
        ("iq", "IQ Test"),
        ("math", "Matematika"),
        ("english", "Ingliz tili"),
        ("native", "Ona tili va Adabiyot"),
    ]

    code = models.CharField(max_length=20, choices=CATEGORY_CHOICES, unique=True)
    name_uz = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    name_ru = models.CharField(max_length=100)
    description_uz = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, default="Brain")
    color = models.CharField(max_length=30, blank=True, default="indigo")
    duration_seconds = models.PositiveIntegerField(default=40 * 60)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Test kategoriyasi"
        verbose_name_plural = "Test kategoriyalari"

    def __str__(self):
        return self.name_uz


class Question(models.Model):
    CATEGORY_CHOICES = [
        ("pattern", "Pattern Recognition & Matrix"),
        ("spatial", "Spatial Visualization"),
        ("numerical", "Numerical Sequences"),
        ("abstract", "Abstract Reasoning"),
        ("algebra", "Algebra"),
        ("geometry", "Geometry"),
        ("arithmetic", "Arithmetic"),
        ("logic", "Logic"),
        ("grammar", "Grammar"),
        ("vocabulary", "Vocabulary"),
        ("reading", "Reading"),
        ("ortography", "Ortografiya"),
        ("literature", "Adabiyot"),
        ("grammar_uz", "Grammatika"),
        ("analysis", "Tahlil"),
    ]

    test_type = models.ForeignKey(
        TestCategory,
        on_delete=models.CASCADE,
        related_name="questions",
        null=True,
        blank=True,
    )

    question_text = models.TextField()
    explanation = models.TextField(blank=True)
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)

    image_url = models.TextField(blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
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

    test_category = models.ForeignKey(
        TestCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sessions",
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

    correct_count = models.PositiveIntegerField(default=0)
    wrong_count = models.PositiveIntegerField(default=0)
    unanswered_count = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)

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


# ═══════════════════════════════════════════
# IMAGE QUESTION — Bolalar uchun rasm savoli
# ═══════════════════════════════════════════
class ImageQuestion(models.Model):
    """
    Bolalar uchun rasm savoli:
    - 30+ rasm (emoji yoki URL)
    - Bittasi noto'g'ri
    - Foydalanuvchi o'sha rasmni bosadi
    """
    question_text = models.TextField(
        blank=True,
        default="Boshqalarga o'xshamagan rasmni toping",
    )
    hint_text = models.CharField(max_length=200, blank=True)

    # Rasmlar ro'yxati (emoji yoki URL)
    images = models.JSONField(default=list)

    # To'g'ri javob indeksi
    correct_index = models.PositiveIntegerField()

    explanation = models.TextField(blank=True)
    difficulty = models.FloatField(default=1.0)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Rasm savoli"
        verbose_name_plural = "Rasm savollari"

    def __str__(self):
        return f"Image Q{self.order}: {len(self.images)} images"