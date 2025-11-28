# TAGMATCH urls

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("landing", views.landing, name="landing"),
    path("home", views.home, name="home"),
    # path("pathname", views.name, name="pageurl.html"),
    # path("pathname", views.name, name="pageurl.html"),
    # path("pathname", views.name, name="pageurl.html"),
    # path("pathname", views.name, name="pageurl.html"),
    # path("pathname", views.name, name="pageurl.html"),
    # path("pathname", views.name, name="pageurl.html"),
    path("admin/", admin.site.urls),
    path("login", views.login, name="login"),
    path("profiles/", include("profiles.urls"))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # appends URL patterns so Django can serve user-uploaded media files