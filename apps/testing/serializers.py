from rest_framework import serializers
from .models import Question, TestSession, TestCategory, ImageQuestion


class TestCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCategory
        fields = [
            "id", "code", "name_uz", "name_en", "name_ru",
            "description_uz", "icon", "color", "duration_seconds", "order",
        ]


class LocalizedQuestionSerializer(serializers.ModelSerializer):
    text = serializers.CharField(source="question_text")
    options = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ["id", "text", "options", "image_url", "category", "difficulty", "order"]

    def get_options(self, obj):
        return [obj.option_a, obj.option_b, obj.option_c, obj.option_d]


class UserAnswerInputSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_index = serializers.IntegerField(
        min_value=0, max_value=3, required=False, allow_null=True
    )
    time_spent = serializers.IntegerField(min_value=0, default=0)


class SubmitTestSerializer(serializers.Serializer):
    session_uuid = serializers.UUIDField()
    answers = UserAnswerInputSerializer(many=True)


class SessionResultSerializer(serializers.ModelSerializer):
    test_category = TestCategorySerializer(read_only=True)

    class Meta:
        model = TestSession
        fields = [
            "uuid", "status", "language", "test_category",
            "started_at", "finished_at", "duration_seconds",
            "raw_score", "accuracy", "iq_score", "percentile",
            "category_breakdown",
            "correct_count", "wrong_count", "unanswered_count",
            "total_questions",
        ]


# ═══════════════════════════════════════════
# IMAGE QUESTION SERIALIZERS
# ═══════════════════════════════════════════
class ImageQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageQuestion
        fields = [
            "id", "question_text", "hint_text", "images",
            "difficulty", "order",
        ]


class ImageAnswerInputSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_index = serializers.IntegerField(
        min_value=0, required=False, allow_null=True
    )
    time_spent = serializers.IntegerField(min_value=0, default=0)


class SubmitImageTestSerializer(serializers.Serializer):
    answers = ImageAnswerInputSerializer(many=True)