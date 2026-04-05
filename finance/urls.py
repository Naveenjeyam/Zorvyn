from django.urls import path
from .views import (
    CategoryListCreateView,
    CategoryDetailView,
    FinancialRecordListCreateView,
    FinancialRecordDetailView,
)
urlpatterns = [
    path("categories/", CategoryListCreateView.as_view(), name="category-list-create"),
    path("categories/<int:pk>/", CategoryDetailView.as_view(), name="category-detail"),
    path("records/", FinancialRecordListCreateView.as_view(), name="record-list-create"),
    path("records/<int:pk>/", FinancialRecordDetailView.as_view(), name="record-detail"),
]
