# PROFILES urls

from django.urls import path
from . import views

urlpatterns = [
    path("edit/", views.edit_profile, name="edit_profile"),
    path("profile/", views.profile, name="profile_self"),
    path("profile/<str:username>/", views.profile_view, name="profile"),
    path("gallery/<str:username>/", views.gallery_view, name="gallery_view"),
    path("update-tags/", views.update_tags, name="update_tags"),
]
