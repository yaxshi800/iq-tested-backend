from uuid import uuid4

from django.utils.timezone import now
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Question, TestSession
from .serializers import (
    LocalizedQuestionSerializer,
    SubmitTestSerializer,
    SessionResultSerializer,
)
from .scoring import compute_result


# ─────────────────── TEST START ───────────────────
@api_view(["POST"])
@permission_classes([AllowAny])
def start_test(request):
    """Test boshlash. Login talab qilinmaydi."""
    questions = Question.objects.filter(is_active=True).order_by("order")[:40]

    session = TestSession.objects.create(
        language="uz",
        user=request.user if request.user.is_authenticated else None,
    )
    serializer = LocalizedQuestionSerializer(questions, many=True)

    return Response(
        {
            "session_uuid": str(session.uuid),
            "language": "uz",
            "duration_seconds": 40 * 60,
            "total_questions": len(serializer.data),
            "questions": serializer.data,
            "message": "Test session created. Good luck!",
        },
        status=status.HTTP_201_CREATED,
    )


# ─────────────────── TEST SUBMIT ───────────────────
@api_view(["POST"])
@permission_classes([AllowAny])
def submit_test(request):
    """Javoblarni yuborish. Login talab qilinmaydi."""
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
    session.status = "completed"
    session.finished_at = now()
    session.save()

    return Response(
        {
            "message": "Test completed successfully.",
            "result": SessionResultSerializer(session).data,
        }
    )


# ─────────────────── RESULTS ───────────────────
@api_view(["GET"])
@permission_classes([AllowAny])
def get_results(request, uuid):
    """Natijani olish."""
    try:
        session = TestSession.objects.get(uuid=uuid)
    except TestSession.DoesNotExist:
        return Response({"detail": "Session not found."}, status=404)
    return Response(SessionResultSerializer(session).data)


# ─────────────────── ISSUE CERTIFICATE ───────────────────
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def issue_certificate(request, uuid):
    """
    Sertifikat berish. Faqat Pro/Ultimate foydalanuvchilar uchun.
    Profilida F.I.SH, pasport, telefon bo'lishi kerak.
    """
    profile = request.user.profile

    # ─── Tarif tekshiruvi ───
    if not profile.is_pro and not profile.is_ultimate:
        return Response(
            {
                "detail": "Sertifikat olish uchun Pro yoki Ultimate tarifga o‘tish kerak.",
                "requires_subscription": True,
            },
            status=403,
        )

    try:
        session = TestSession.objects.get(uuid=uuid, user=request.user)
    except TestSession.DoesNotExist:
        return Response({"detail": "Sessiya topilmadi."}, status=404)

    if session.status != "completed":
        return Response({"detail": "Test tugallanmagan."}, status=400)

    if not profile.is_certificate_ready:
        return Response(
            {"detail": "Sertifikat uchun F.I.SH, pasport va telefon raqami kerak."},
            status=400,
        )

    if not profile.certificate_uuid:
        profile.certificate_uuid = uuid4()
        profile.certificate_issued = True
        profile.save()

    profile.certificate_downloads += 1
    profile.save()

    return Response(
        {
            "certificate_uuid": str(profile.certificate_uuid),
            "iq_score": session.iq_score,
            "percentile": session.percentile,
            "issued_at": timezone.now(),
            "plan": profile.plan,
        }
    )


# ─────────────────── VERIFY CERTIFICATE ─────────────────── ✅ YANGI
@api_view(["GET"])
@permission_classes([AllowAny])
def verify_certificate(request, cert_uuid):
    """
    Sertifikat tekshiruvi. Login talab qilinmaydi.
    Ommaviy — har kim sertifikat haqiqiyligini tekshirishi mumkin.
    """
    from apps.accounts.models import Profile

    try:
        profile = Profile.objects.get(certificate_uuid=cert_uuid)
    except Profile.DoesNotExist:
        return Response(
            {"valid": False, "detail": "Sertifikat topilmadi."},
            status=404,
        )

    if not profile.certificate_issued:
        return Response(
            {"valid": False, "detail": "Sertifikat hali berilmagan."},
            status=404,
        )

    # Eng so'nggi tugallangan sessiya
    latest_session = (
        profile.user.test_sessions.filter(status="completed")
        .order_by("-finished_at")
        .first()
    )

    return Response(
        {
            "valid": True,
            "full_name": profile.full_name,
            "issued_at": profile.updated_at,
            "iq_score": latest_session.iq_score if latest_session else None,
            "percentile": latest_session.percentile if latest_session else None,
            "plan": profile.plan,
            "certificate_uuid": str(profile.certificate_uuid),
        }
    )