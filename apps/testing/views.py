from uuid import uuid4
from datetime import date, timedelta
from django.utils.timezone import now
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
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


def update_streak_and_achievements(user, session):
    """Test tugagandan keyin streak va achievements yangilash"""
    if not user or not user.is_authenticated:
        return []

    from apps.accounts.models import Achievement, UserAchievement, DailyStreak

    streak, _ = DailyStreak.objects.get_or_create(user=user)
    today = date.today()

    # Streak mantiqiy
    if streak.last_activity == today:
        pass
    elif streak.last_activity == today - timedelta(days=1):
        streak.current_streak += 1
        streak.longest_streak = max(streak.longest_streak, streak.current_streak)
    else:
        streak.current_streak = 1

    streak.last_activity = today

    earned = []

    # 1. Birinchi test
    ach = Achievement.objects.filter(code="first_test").first()
    if ach and not UserAchievement.objects.filter(user=user, achievement=ach).exists():
        UserAchievement.objects.create(user=user, achievement=ach)
        streak.total_points += ach.points
        earned.append(ach.name_uz)

    # 2. Mukammal natija
    if session.accuracy == 1.0:
        ach = Achievement.objects.filter(code="perfect_score").first()
        if ach and not UserAchievement.objects.filter(user=user, achievement=ach).exists():
            UserAchievement.objects.create(user=user, achievement=ach)
            streak.total_points += ach.points
            earned.append(ach.name_uz)

    # 3. IQ ustasi
    if session.iq_score and session.iq_score >= 120:
        ach = Achievement.objects.filter(code="iq_master").first()
        if ach and not UserAchievement.objects.filter(user=user, achievement=ach).exists():
            UserAchievement.objects.create(user=user, achievement=ach)
            streak.total_points += ach.points
            earned.append(ach.name_uz)

    # 4. 7 kunlik streak
    if streak.current_streak >= 7:
        ach = Achievement.objects.filter(code="seven_day_streak").first()
        if ach and not UserAchievement.objects.filter(user=user, achievement=ach).exists():
            UserAchievement.objects.create(user=user, achievement=ach)
            streak.total_points += ach.points
            earned.append(ach.name_uz)

    streak.save()
    return earned


@api_view(["GET"])
@permission_classes([AllowAny])
def test_categories(request):
    cats = TestCategory.objects.filter(is_active=True)
    return Response(TestCategorySerializer(cats, many=True).data)


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

    # Har bir test uchun 30 savol, faqat "teacher" uchun 20
    limit = 20 if category_code == "teacher" else 30

    questions = Question.objects.filter(
        test_type=test_cat, is_active=True
    ).order_by("order")[:limit]

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

    # Streak va achievements
    earned = update_streak_and_achievements(request.user, session)

    return Response({
        "message": "Test completed successfully.",
        "result": SessionResultSerializer(session).data,
        "earned_achievements": earned or [],
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def get_results(request, uuid):
    try:
        session = TestSession.objects.get(uuid=uuid)
    except TestSession.DoesNotExist:
        return Response({"detail": "Session not found."}, status=404)
    return Response(SessionResultSerializer(session).data)


# ═══════════════════════════════════════════
# IMAGE TEST
# ═══════════════════════════════════════════
@api_view(["POST"])
@permission_classes([AllowAny])
def start_image_test(request):
    questions = ImageQuestion.objects.filter(is_active=True).order_by("order")[:20]

    if not questions.exists():
        return Response(
            {"detail": "Rasm savollari topilmadi."},
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


@api_view(["POST"])
@permission_classes([AllowAny])
def submit_image_test(request):
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