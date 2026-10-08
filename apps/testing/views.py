from uuid import uuid4

from django.utils.timezone import now
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Question, TestSession, TestCategory, ImageQuestion
from .serializers import (
    LocalizedQuestionSerializer,
    SubmitTestSerializer,
    SessionResultSerializer,
    TestCategorySerializer,
    ImageQuestionSerializer,
    SubmitImageTestSerializer,
)
from .scoring import compute_result


# ═══════════════════════════════════════════
# TEST CATEGORIES
# ═══════════════════════════════════════════
@api_view(["GET"])
@permission_classes([AllowAny])
def test_categories(request):
    cats = TestCategory.objects.filter(is_active=True)
    serializer = TestCategorySerializer(cats, many=True)
    return Response(serializer.data)


# ═══════════════════════════════════════════
# TEST START (oddiy testlar)
# ═══════════════════════════════════════════
@api_view(["POST"])
@permission_classes([AllowAny])
def start_test(request):
    category_code = request.data.get("category", "iq")

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
# TEST SUBMIT (oddiy testlar)
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


# ═══════════════════════════════════════════
# IMAGE TEST — START
# ═══════════════════════════════════════════
@api_view(["POST"])
@permission_classes([AllowAny])
def start_image_test(request):
    """
    Rasm savollari testini boshlash.
    Maksimum 20 ta savol qaytaradi.
    """
    questions = ImageQuestion.objects.filter(is_active=True).order_by("order")[:20]

    if not questions.exists():
        return Response(
            {"detail": "Rasm savollari topilmadi. Iltimos, admin panelda qo'shing."},
            status=404,
        )

    serializer = ImageQuestionSerializer(questions, many=True)

    return Response(
        {
            "language": "uz",
            "total_questions": len(serializer.data),
            "questions": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ═══════════════════════════════════════════
# IMAGE TEST — SUBMIT
# ═══════════════════════════════════════════
@api_view(["POST"])
@permission_classes([AllowAny])
def submit_image_test(request):
    """
    Rasm testi javoblarini qabul qilish va natijani qaytarish.
    """
    serializer = SubmitImageTestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    answers = serializer.validated_data["answers"]

    questions = {q.id: q for q in ImageQuestion.objects.filter(is_active=True)}

    correct = 0
    wrong = 0
    unanswered = 0
    details = []

    for ans in answers:
        q = questions.get(ans["question_id"])
        if not q:
            continue

        selected = ans.get("selected_index")

        if selected is None:
            unanswered += 1
            details.append({
                "question_id": q.id,
                "selected_index": None,
                "correct_index": q.correct_index,
                "is_correct": False,
            })
            continue

        is_correct = selected == q.correct_index
        if is_correct:
            correct += 1
        else:
            wrong += 1

        details.append({
            "question_id": q.id,
            "selected_index": selected,
            "correct_index": q.correct_index,
            "is_correct": is_correct,
        })

    total = len(answers)
    percentage = round((correct / total * 100) if total else 0, 1)

    return Response({
        "total_questions": total,
        "correct_count": correct,
        "wrong_count": wrong,
        "unanswered_count": unanswered,
        "percentage": percentage,
        "details": details,
    }, status=status.HTTP_200_OK)