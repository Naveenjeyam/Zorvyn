from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from core import views
from django.shortcuts import render

schema_view = get_schema_view(
    openapi.Info(
        title="Finance Dashboard API",
        default_version="v1",
        description="Finance Dashboard Backend API",
    ),
    public=True,
    permission_classes=[AllowAny],
)

def index(request):
    return render(request, 'index.html')

def run_seed(request):
    """
    One-time seed endpoint. Call this from browser to seed the database.
    DELETE this endpoint after seeding is done.
    """
    import os
    secret = request.GET.get("key", "")
    if secret != os.getenv("SEED_KEY", "seed-finance-2024"):
        return JsonResponse({"error": "Invalid key"}, status=403)

    try:
        from django.contrib.auth import get_user_model
        from finance.models import Category, FinancialRecord
        from datetime import date, timedelta
        import random
        import decimal

        User = get_user_model()
        created = []

        # Create users
        users_data = [
            {"email": "admin@finance.com",    "password": "Admin@1234",    "full_name": "Admin User",    "role": "admin",    "is_staff": True},
            {"email": "analyst@finance.com",  "password": "Analyst@1234",  "full_name": "Analyst User",  "role": "analyst"},
            {"email": "viewer@finance.com",   "password": "Viewer@1234",   "full_name": "Viewer User",   "role": "viewer"},
        ]
        for u in users_data:
            if not User.objects.filter(email=u["email"]).exists():
                User.objects.create_user(**u)
                created.append(f"User: {u['email']}")

        # Create categories
        cat_names = ["Salary","Freelance","Rent","Food & Groceries","Utilities","Transport","Healthcare","Entertainment","Investments","Miscellaneous"]
        cat_objects = {}
        for name in cat_names:
            cat, _ = Category.objects.get_or_create(name=name)
            cat_objects[name] = cat

        # Create records
        admin_user = User.objects.get(email="admin@finance.com")
        record_count = FinancialRecord.objects.count()

        if record_count == 0:
            income_cats  = ["Salary", "Freelance", "Investments"]
            expense_cats = ["Rent", "Food & Groceries", "Utilities", "Transport", "Healthcare", "Entertainment", "Miscellaneous"]
            records = []
            today = date.today()

            for i in range(60):
                is_income   = random.random() < 0.4
                record_date = today - timedelta(days=random.randint(0, 180))
                cat_name    = random.choice(income_cats if is_income else expense_cats)
                records.append(FinancialRecord(
                    amount      = decimal.Decimal(str(round(random.uniform(500, 50000), 2))),
                    type        = "income" if is_income else "expense",
                    category    = cat_objects[cat_name],
                    date        = record_date,
                    notes       = f"Sample record {i + 1}",
                    created_by  = admin_user,
                ))
            FinancialRecord.objects.bulk_create(records)
            created.append(f"60 financial records")

        return JsonResponse({
            "status": "success",
            "created": created,
            "total_users": User.objects.count(),
            "total_records": FinancialRecord.objects.count(),
            "total_categories": Category.objects.count(),
        })

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index,name="index"),
    path("api/auth/", include("core.urls")),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/finance/", include("finance.urls")),
    path("api/dashboard/", include("dashboard.urls")),
    path("api/docs/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger-ui"),
    path("api/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="redoc"),
]