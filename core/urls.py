# core/urls.py — should look like this
from django.urls import path
from .views import (
    LoginView,      # ← your custom EmailTokenObtainPairView
    RegisterView,
    LogoutView,
    ProfileView,
    ChangePasswordView,
    UserListCreateView,
    UserDetailView,
)

urlpatterns = [
    path('login/',           LoginView.as_view(),          name='login'),
    path('register/',        RegisterView.as_view(),        name='register'),
    path('logout/',          LogoutView.as_view(),          name='logout'),
    path('profile/',         ProfileView.as_view(),         name='profile'),
    path('change-password/', ChangePasswordView.as_view(),  name='change-password'),
    path('users/',           UserListCreateView.as_view(),  name='user-list'),
    path('users/<int:pk>/',  UserDetailView.as_view(),      name='user-detail'),
]