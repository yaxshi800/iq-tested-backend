from django.contrib import admin
from django.utils.html import format_html
from .models import Question, TestSession, UserAnswer


# ═══════════════════════════════════════════
# QUESTION ADMIN
# ═══════════════════════════════════════════
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "short_text",
        "category_badge",
        "difficulty_display",
        "correct_display",
        "order",
        "is_active",
    )
    list_filter = ("category", "is_active", "difficulty")
    search_fields = ("question_text", "explanation")
    ordering = ("order", "id")
    list_editable = ("order", "is_active")
    list_per_page = 25

    fieldsets = (
        ("Savol", {
            "fields": ("question_text", "image_url", "explanation")
        }),
        ("Javob variantlari", {
            "fields": ("option_a", "option_b", "option_c", "option_d")
        }),
        ("To'g'ri javob", {
            "fields": ("correct_index",)
        }),
        ("Meta", {
            "fields": ("category", "difficulty", "order", "is_active")
        }),
    )

    def short_text(self, obj):
        return obj.question_text[:60] + "..." if len(obj.question_text) > 60 else obj.question_text

    short_text.short_description = "Savol"

    def category_badge(self, obj):
        colors = {
            "pattern": "#6366f1",
            "spatial": "#10b981",
            "numerical": "#f59e0b",
            "abstract": "#ec4899",
        }
        labels = {
            "pattern": "Pattern",
            "spatial": "Spatial",
            "numerical": "Numerical",
            "abstract": "Abstract",
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            colors.get(obj.category, "#64748b"),
            labels.get(obj.category, obj.category),
        )

    category_badge.short_description = "Kategoriya"

    def difficulty_display(self, obj):
        stars = "⭐" * int(obj.difficulty)
        return format_html(
            '<span style="font-size:11px;">{} <span style="color:#94a3b8;">{}</span></span>',
            stars,
            obj.difficulty,
        )

    difficulty_display.short_description = "Qiyinlik"

    def correct_display(self, obj):
        letters = ["A", "B", "C", "D"]
        return format_html(
            '<span style="background:#10b981;color:white;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            letters[obj.correct_index],
        )

    correct_display.short_description = "To'g'ri javob"


# ═══════════════════════════════════════════
# USER ANSWER INLINE
# ═══════════════════════════════════════════
class UserAnswerInline(admin.TabularInline):
    model = UserAnswer
    extra = 0
    can_delete = False
    readonly_fields = ("question", "selected_index", "time_spent", "is_correct")
    fields = ("question", "selected_index", "time_spent", "is_correct")

    def has_add_permission(self, request, obj=None):
        return False


# ═══════════════════════════════════════════
# TEST SESSION ADMIN
# ═══════════════════════════════════════════
@admin.register(TestSession)
class TestSessionAdmin(admin.ModelAdmin):
    list_display = (
        "uuid_short",
        "user_display",
        "status_badge",
        "iq_display",
        "percentile_display",
        "duration_display",
        "started_at",
    )
    list_filter = ("status", "language", "started_at")
    search_fields = ("uuid", "user__username")
    readonly_fields = (
        "uuid",
        "user",
        "started_at",
        "finished_at",
        "duration_seconds",
        "raw_score",
        "accuracy",
        "iq_score",
        "percentile",
        "category_breakdown",
    )
    ordering = ("-started_at",)
    date_hierarchy = "started_at"
    inlines = [UserAnswerInline]

    fieldsets = (
        ("Sessiya", {
            "fields": ("uuid", "user", "language", "status")
        }),
        ("Vaqt", {
            "fields": ("started_at", "finished_at", "duration_seconds")
        }),
        ("Natija", {
            "fields": ("raw_score", "accuracy", "iq_score", "percentile")
        }),
        ("Batafsil", {
            "fields": ("category_breakdown",),
            "classes": ("collapse",)
        }),
    )

    def uuid_short(self, obj):
        return format_html(
            '<span style="font-family:monospace;font-size:11px;">{}…</span>',
            str(obj.uuid)[:8],
        )

    uuid_short.short_description = "UUID"

    def user_display(self, obj):
        if obj.user:
            return format_html(
                '<a href="/admin/auth/user/{}/change/" style="color:#6366f1;font-weight:600;">{}</a>',
                obj.user.id,
                obj.user.username,
            )
        return format_html('<span style="color:#94a3b8;">Anonim</span>')

    user_display.short_description = "Foydalanuvchi"

    def status_badge(self, obj):
        colors = {
            "in_progress": "#f59e0b",
            "completed": "#10b981",
            "expired": "#ef4444",
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            colors.get(obj.status, "#64748b"),
            obj.status.replace("_", " ").upper(),
        )

    status_badge.short_description = "Holat"

    def iq_display(self, obj):
        if obj.iq_score is None:
            return "—"
        return format_html(
            '<span style="font-weight:700;font-size:14px;color:#6366f1;">{}</span>',
            obj.iq_score,
        )

    iq_display.short_description = "IQ"

    def percentile_display(self, obj):
        if obj.percentile is None:
            return "—"
        return format_html(
            '<span style="color:#10b981;font-weight:600;">{}%</span>',
            obj.percentile,
        )

    percentile_display.short_description = "Persentil"

    def duration_display(self, obj):
        seconds = obj.duration_seconds or 0
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"

    duration_display.short_description = "Davomiylik"

    # Faqat ko'rish
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ═══════════════════════════════════════════
# USER ANSWER ADMIN
# ═══════════════════════════════════════════
@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = (
        "session_short",
        "question_short",
        "selected_index",
        "is_correct_display",
        "time_spent",
    )
    list_filter = ("is_correct",)
    search_fields = ("session__uuid", "question__question_text")
    readonly_fields = ("session", "question", "selected_index", "time_spent", "is_correct")

    def session_short(self, obj):
        return str(obj.session.uuid)[:8]

    session_short.short_description = "Sessiya"

    def question_short(self, obj):
        return obj.question.question_text[:40] + "..."

    question_short.short_description = "Savol"

    def is_correct_display(self, obj):
        if obj.is_correct:
            return format_html('<span style="color:#10b981;font-weight:700;">✓</span>')
        return format_html('<span style="color:#ef4444;font-weight:700;">✗</span>')

    is_correct_display.short_description = "To'g'ri"