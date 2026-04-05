from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
schema_view = get_schema_view(
    openapi.Info(
        title="Finance Dashboard API",
        default_version="v1",
        description="Role-based Finance Dashboard Backend API",
        contact=openapi.Contact(email="admin@finance.com"),
    ),
    public=True,
    permission_classes=[AllowAny],
)
def health(request):
    """Simple health check endpoint."""
    return JsonResponse({"status": "ok", "message": "Finance API is running."})
urlpatterns = [

    path("", health),
    path("health/", health),
    path("admin/", admin.site.urls),
    path("api/auth/login",include("index")),
    path("api/auth/", include("core.urls")),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/finance/", include("finance.urls")),
    path("api/dashboard/", include("dashboard.urls")),
    path("api/docs/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger-ui"),
    path("api/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="redoc"),
]