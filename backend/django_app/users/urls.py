from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, ProfileView, ChangePasswordView, generate_api_key, user_stats

urlpatterns = [
    path("register/", RegisterView.as_view(), name="user-register"),
    path("login/", TokenObtainPairView.as_view(), name="token-obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("profile/", ProfileView.as_view(), name="user-profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("api-key/", generate_api_key, name="generate-api-key"),
    path("stats/", user_stats, name="user-stats"),
]
