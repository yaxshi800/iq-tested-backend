import uuid as uuid_lib

from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Payment
from .card_utils import detect_card_type, luhn_check
from .serializers import (
    RegisterSerializer, ProfileSerializer, UserSerializer,
    PaymentSerializer, PaymentRequestSerializer,
)


PLAN_PRICES = {
    "pro": {"amount": 49000, "currency": "UZS", "days": 30, "label": "Pro (1 oy)"},
    "ultimate": {"amount": 149000, "currency": "UZS", "days": 90, "label": "Ultimate (3 oy)"},
}


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    profile = request.user.profile
    serializer = ProfileSerializer(profile, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def plan_prices(request):
    return Response(PLAN_PRICES)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def process_payment(request):
    serializer = PaymentRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    plan = data["plan"]
    card_number = data["card_number"]

    if not luhn_check(card_number):
        return Response(
            {"detail": "Karta raqami noto‘g‘ri."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    card_type = detect_card_type(card_number)
    if card_type == "unknown":
        return Response(
            {"detail": "Karta turi aniqlanmadi."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    plan_info = PLAN_PRICES[plan]
    digits = "".join(c for c in card_number if c.isdigit())

    payment = Payment.objects.create(
        user=request.user,
        plan=plan,
        amount=plan_info["amount"],
        currency=plan_info["currency"],
        card_type=card_type,
        card_last4=digits[-4:],
        card_holder=data["card_holder"],
        transaction_id=str(uuid_lib.uuid4()).replace("-", "")[:32].upper(),
        status="success",
        completed_at=timezone.now(),
        admin_account=getattr(settings, "ADMIN_PAYMENT_ACCOUNT", ""),
    )

    request.user.profile.activate_plan(plan, days=plan_info["days"])

    return Response(
        {
            "message": f"{plan_info['label']} faollashtirildi!",
            "payment": PaymentSerializer(payment).data,
            "user": UserSerializer(request.user).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_payments(request):
    payments = Payment.objects.filter(user=request.user)
    return Response(PaymentSerializer(payments, many=True).data)