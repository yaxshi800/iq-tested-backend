from uuid import uuid4

from django.utils.timezone import now
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Question, TestSession, TestCategory
from .serializers import (
    LocalizedQuestionSerializer,
    SubmitTestSerializer,
    SessionResultSerializer,
    TestCategorySerializer,
)
from .scoring import compute_result


# ═══════════════════════════════════════════
# TEST CATEGORIES — 4 ta test turi
# ═══════════════════════════════════════════
@api_view(["GET"])
@permission_classes([AllowAny])
def test_categories(request):
    """Barcha test turlarini olish."""
    cats = TestCategory.objects.filter(is_active=True)
    serializer = TestCategorySerializer(cats, many=True)
    return Response(serializer.data)


# ═══════════════════════════════════════════
# TEST START
# ═══════════════════════════════════════════
@api_view(["POST"])
@permission_classes([AllowAny])
def start_test(request):
    category_code = request.data.get("category", "iq")

    # ═══════════════════════════════════════════
    # ARALASH TEST
    # ═══════════════════════════════════════════
    if category_code == "mixed":
        import random

        # Har bir turdan nechta savol olamiz
        per_category = {
            "iq": 10,
            "math": 10,
            "english": 10,
            "native": 10,
        }

        all_questions = []
        for cat_code, count in per_category.items():
            try:
                test_cat = TestCategory.objects.get(code=cat_code, is_active=True)
                qs = list(
                    Question.objects.filter(test_type=test_cat, is_active=True)
                )
                random.shuffle(qs)
                all_questions.extend(qs[:count])
            except TestCategory.DoesNotExist:
                continue

        # Aralashtirish
        random.shuffle(all_questions)

        if not all_questions:
            return Response(
                {"detail": "Aralash test uchun savollar topilmadi."},
                status=404,
            )

        # Aralash test uchun maxsus kategoriya (vaqtincha)
        session = TestSession.objects.create(
            language="uz",
            user=request.user if request.user.is_authenticated else None,
            test_category=None,  # Aralash — maxsus kategoriya yo'q
        )

        serializer = LocalizedQuestionSerializer(all_questions, many=True)

        return Response(
            {
                "session_uuid": str(session.uuid),
                "language": "uz",
                "category": {
                    "code": "mixed",
                    "name_uz": "Aralash Test",
                    "name_en": "Mixed Test",
                    "name_ru": "Смешанный тест",
                    "description_uz": "Barcha turdagi aralash savollar",
                    "icon": "Sparkles",
                    "color": "rose",
                    "duration_seconds": 40 * 60,
                },
                "duration_seconds": 40 * 60,
                "total_questions": len(serializer.data),
                "questions": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    # ═══════════════════════════════════════════
    # ODDIY TEST (IQ, Matematika, Ingliz, Ona tili)
    # ═══════════════════════════════════════════
    try:
        test_cat = TestCategory.objects.get(code=category_code, is_active=True)
    except TestCategory.DoesNotExist:
        return Response(
            {"detail": f"Test turi '{category_code}' topilmadi."},
            status=404,
        )

    questions = Question.objects.filter(
        test_type=test_cat, is_active=True
    ).order_by("order")[:40]

    if not questions.exists():
        return Response(
            {"detail": f"'{test_cat.name_uz}' uchun savollar topilmadi."},
            status=404,
        )

    session = TestSession.objects.create(
        language="uz",
        user=request.user if request.user.is_authenticated else None,
        test_category=test_cat,
    )

    serializer = LocalizedQuestionSerializer(questions, many=True)

    return Response(
        {
            "session_uuid": str(session.uuid),
            "language": "uz",
            "category": TestCategorySerializer(test_cat).data,
            "duration_seconds": test_cat.duration_seconds,
            "total_questions": len(serializer.data),
            "questions": serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )

# ═══════════════════════════════════════════
# TEST SUBMIT
# ═══════════════════════════════════════════
@api_view(["POST"])
@permission_classes([AllowAny])
def submit_test(request):
    serializer = SubmitTestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    try:
        session = TestSession.objects.get(uuid=data["session_uuid"])
    except TestSession.DoesNotExist:
        return Response({"detail": "Session not found."}, status=404)

    if session.status == "completed":
        return Response(SessionResultSerializer(session).data)

    result = compute_result(session, data["answers"])

    session.raw_score = result["raw_score"]
    session.accuracy = result["accuracy"]
    session.iq_score = result["iq_score"]
    session.percentile = result["percentile"]
    session.category_breakdown = result["category_breakdown"]
    session.duration_seconds = result["duration_seconds"]
    session.correct_count = result["correct_count"]
    session.wrong_count = result["wrong_count"]
    session.unanswered_count = result["unanswered_count"]
    session.total_questions = result["total_questions"]
    session.status = "completed"
    session.finished_at = now()
    session.save()

    return Response({
        "message": "Test completed successfully.",
        "result": SessionResultSerializer(session).data,
    })


# ═══════════════════════════════════════════
# GET RESULTS
# ═══════════════════════════════════════════
@api_view(["GET"])
@permission_classes([AllowAny])
def get_results(request, uuid):
    try:
        session = TestSession.objects.get(uuid=uuid)
    except TestSession.DoesNotExist:
        return Response({"detail": "Session not found."}, status=404)
    return Response(SessionResultSerializer(session).data)