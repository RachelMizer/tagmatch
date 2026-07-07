# PROFILES models.py

from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth.models import User
from PIL import Image, ImageOps
from taggit.managers import TaggableManager
import io

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Profile image
    image = models.ImageField(
        upload_to='profile_images/',
        blank=True,
        null=True
    )

    # Basic info
    location = models.CharField(max_length=100, blank=True, null=True)
    gender_identity = models.CharField(max_length=50, blank=True, null=True)
    sexuality = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    height_feet = models.IntegerField(null=True, blank=True)
    height_inches = models.IntegerField(null=True, blank=True)
    build = models.CharField(max_length=50, blank=True, null=True)
    children_status = models.CharField(max_length=50, blank=True, null=True)

    # Relationship types
    relationship_types_seeking = models.JSONField(blank=True, null=True)

    # Tag System
    tags = TaggableManager()
    created_at = models.DateTimeField(auto_now_add=True)

    TIME_FORMAT_CHOICES = [
        ('12hr', '12-hour (AM/PM)'),
        ('24hr', '24-hour'),
    ]
    time_format = models.CharField(max_length=4, choices=TIME_FORMAT_CHOICES, default='12hr')
    email_verified = models.BooleanField(default=False)
    is_support = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s profile"

    @property
    def avatar_url(self):
        if self.image:
            return self.image.url
        return "/static/img/default_profile.png"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Only process if an actual uploaded file exists. Read/write through the
        # storage API (not self.image.path) so this works on remote backends like
        # Azure Blob Storage, which don't support local filesystem paths.
        if self.image:
            try:
                self.image.open("rb")
                img = Image.open(self.image)
                original_format = img.format or "JPEG"
                img = ImageOps.exif_transpose(img)

                # Crop to square
                width, height = img.size
                min_dim = min(width, height)
                left = (width - min_dim) / 2
                top = (height - min_dim) / 2
                right = (width + min_dim) / 2
                bottom = (height + min_dim) / 2
                img = img.crop((left, top, right, bottom))

                # Resize to 500x500
                img = img.resize((500, 500), Image.LANCZOS)

                # JPEG can't encode an alpha channel (e.g. PNGs with transparency).
                if original_format == "JPEG" and img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                buffer = io.BytesIO()
                img.save(buffer, format=original_format)
                self.image.close()

                self.image.storage.delete(self.image.name)
                self.image.storage.save(self.image.name, ContentFile(buffer.getvalue()))

            except FileNotFoundError:
                pass


class Block(models.Model):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocking')
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')

    def __str__(self):
        return f"{self.blocker.username} blocked {self.blocked.username}"


class Report(models.Model):
    REASON_CHOICES = [
        ('harassment', 'Harassment'),
        ('fake_profile', 'Fake Profile'),
        ('inappropriate', 'Inappropriate Content'),
        ('spam', 'Spam'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resolved', 'Resolved — Action Taken'),
        ('dismissed', 'Dismissed — No Violation'),
    ]
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    reported = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_received')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    resolution_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports_resolved')
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.reporter.username} reported {self.reported.username} ({self.reason}) [{self.status}]"

