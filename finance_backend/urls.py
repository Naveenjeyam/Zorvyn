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
    import os
    secret = request.GET.get("key", "")
    expected = os.getenv("SEED_KEY", "seed-finance-2024")
    
    if secret != expected:
        return JsonResponse({
            "error": "Invalid key",
            "provided": secret,
            "hint": "Add SEED_KEY to Render environment variables"
        }, status=403)

    try:
        from django.contrib.auth import get_user_model
        from finance.models import Category, FinancialRecord
        from datetime import date, timedelta
        import random
        import decimal

        User = get_user_model()
        results = []

        # ── Create Admin ──────────────────────────────────────
        if not User.objects.filter(email="admin@finance.com").exists():
            User.objects.create_user(
                email="admin@finance.com",
                password="Admin@1234",
                full_name="Admin User",
                role="admin",
                is_staff=True,
                is_superuser=True,
            )
            results.append("✅ Admin created")
        else:
            # Reset password in case it changed
            u = User.objects.get(email="admin@finance.com")
            u.set_password("Admin@1234")
            u.is_active = True
            u.save()
            results.append("🔄 Admin password reset")

        # ── Create Analyst ────────────────────────────────────
        if not User.objects.filter(email="analyst@finance.com").exists():
            User.objects.create_user(
                email="analyst@finance.com",
                password="Analyst@1234",
                full_name="Analyst User",
                role="analyst",
            )
            results.append("✅ Analyst created")
        else:
            u = User.objects.get(email="analyst@finance.com")
            u.set_password("Analyst@1234")
            u.is_active = True
            u.save()
            results.append("🔄 Analyst password reset")

        # ── Create Viewer ─────────────────────────────────────
        if not User.objects.filter(email="viewer@finance.com").exists():
            User.objects.create_user(
                email="viewer@finance.com",
                password="Viewer@1234",
                full_name="Viewer User",
                role="viewer",
            )
            results.append("✅ Viewer created")
        else:
            u = User.objects.get(email="viewer@finance.com")
            u.set_password("Viewer@1234")
            u.is_active = True
            u.save()
            results.append("🔄 Viewer password reset")

        # ── Create Categories ─────────────────────────────────
        cat_names = [
            "Salary", "Freelance", "Rent",
            "Food & Groceries", "Utilities", "Transport",
            "Healthcare", "Entertainment", "Investments", "Miscellaneous"
        ]
        cat_objects = {}
        for name in cat_names:
            cat, created = Category.objects.get_or_create(name=name)
            cat_objects[name] = cat
        results.append(f"✅ {len(cat_names)} categories ready")

        # ── Create Records ────────────────────────────────────
        admin_user = User.objects.get(email="admin@finance.com")

        if FinancialRecord.objects.count() == 0:
            income_cats  = ["Salary", "Freelance", "Investments"]
            expense_cats = ["Rent", "Food & Groceries", "Utilities",
                           "Transport", "Healthcare", "Entertainment", "Miscellaneous"]
            records = []
            today = date.today()

            for i in range(60):
                is_income   = random.random() < 0.4
                record_date = today - timedelta(days=random.randint(0, 180))
                cat_name    = random.choice(income_cats if is_income else expense_cats)
                records.append(FinancialRecord(
                    amount     = decimal.Decimal(str(round(random.uniform(500, 50000), 2))),
                    type       = "income" if is_income else "expense",
                    category   = cat_objects[cat_name],
                    date       = record_date,
                    notes      = f"Sample record {i + 1}",
                    created_by = admin_user,
                ))

            FinancialRecord.objects.bulk_create(records)
            results.append(f"✅ 60 financial records created")
        else:
            results.append(f"ℹ️ Records already exist: {FinancialRecord.objects.count()}")

        return JsonResponse({
            "status":           "success",
            "results":          results,
            "total_users":      User.objects.count(),
            "total_records":    FinancialRecord.objects.count(),
            "total_categories": Category.objects.count(),
            "login_with": {
                "admin":   "admin@finance.com / Admin@1234",
                "analyst": "analyst@finance.com / Analyst@1234",
                "viewer":  "viewer@finance.com / Viewer@1234",
            }
        })

    except Exception as e:
        import traceback
        return JsonResponse({
            "status":    "error",
            "message":   str(e),
            "traceback": traceback.format_exc(),
        }, status=500)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index,name="index"),
    path("api/auth/", include("core.urls")),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/finance/", include("finance.urls")),
    path("api/dashboard/", include("dashboard.urls")),
    path("api/docs/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger-ui"),
    path("api/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="redoc"),
    path("run-seed/", run_seed, name="run-seed"),
]