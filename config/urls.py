from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


def health_check(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Health check
    path("api/v1/health/", health_check, name="health"),

    # Test endpoints
    path("api/v1/test/", include("apps.testing.urls")),

    # ⭐ Auth endpoints — BU YETISHMAYOTGAN EDI
    path("api/v1/auth/", include("apps.accounts.urls")),

    # JWT token endpoints
    path("api/v1/auth/token/", TokenObtainPairView.as_view(), name="token"),
    path(
        "api/v1/auth/token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),
]