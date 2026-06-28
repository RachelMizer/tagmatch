# tagmatch/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from tagmatch import views as core_views
from profiles import views as profile_views


urlpatterns = [

    # -------------------------
    # Landing + Home
    # -------------------------
    path("", core_views.landing, name="landing"),
    path("landing/", core_views.landing, name="landing"),
    path("home/", core_views.home, name="home"),

    # -------------------------
    # Authentication
    # -------------------------
    path("register/", profile_views.register, name="register"),
    path("login/", core_views.login_view, name="login"),
    path(
        "logout/",
        auth_views.LogoutView.as_view(
            next_page="login",
            http_method_names=["get", "post"]
        ),
        name="logout",
    ),

    # -------------------------
    # User Dashboard Pages
    # -------------------------
    path("messages/", include("messaging.urls")),
    path("matches/", core_views.matches_view, name="matches"),

    # -------------------------
    # Password Reset System
    # -------------------------
    path("password-reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),

    # -------------------------
    # Apps
    # -------------------------
    path("admin/", admin.site.urls),

    # Profiles app (registration, edit profile, etc.)
    path("profiles/", include("profiles.urls")),

    # Logged-in user's own profile
    path("profile/", profile_views.profile, name="my_profile"),

    # View someone else's profile
    path("profile/<str:username>/", profile_views.profile_view, name="profile_view"),

    # Gallery app
    path("gallery/", include("gallery.urls")),

    # -----------------------------
    # Search Page
    # -----------------------------
    path("search/", core_views.search_view, name="search"),

    # -----------------------------
    # Dev
    # -----------------------------
    path("devnotes/", core_views.devnotes, name="devnotes"),
    path("sitemap/", core_views.sitemap, name="sitemap"),
]


# -------------------------
# Media Files (Debug)
# -------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
