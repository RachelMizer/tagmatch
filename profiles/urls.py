# PROFILES urls

from django.urls import path
from . import views

urlpatterns = [
    path("edit/", views.edit_profile, name="edit_profile"),
    path("delete-account/", views.delete_account, name="delete_account"),
    path("profile/", views.profile, name="profile_self"),
    path("profile/<str:username>/", views.profile_view, name="profile"),
    path("gallery/<str:username>/", views.gallery_view, name="gallery_view"),
    path("update-tags/", views.update_tags, name="update_tags"),
    path("block/<str:username>/", views.block_user, name="block_user"),
    path("block/<str:username>/confirm/", views.confirm_block, name="confirm_block"),
    path("unblock/<str:username>/", views.unblock_user, name="unblock_user"),
    path("report/<str:username>/", views.report_user, name="report_user"),
    path("blocked-reported/", views.blocked_reported, name="blocked_reported"),
    path("verify-email/<str:token>/", views.verify_email, name="verify_email"),
    path("resend-verification/", views.resend_verification, name="resend_verification"),
]
