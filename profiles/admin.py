# PROFILES admin.py

from django.contrib import admin
from .models import Profile, Block, Report
from django.utils.html import format_html

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "location", "gender_identity", "sexuality", "children_status", "image_preview")

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return "—"

    image_preview.short_description = "Profile Image"


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ("blocker", "blocked", "created_at")
    list_filter = ("created_at",)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("reporter", "reported", "reason", "status", "created_at", "resolved_by")
    list_filter = ("reason", "status", "created_at")
    readonly_fields = ("reporter", "reported", "reason", "description", "created_at")
