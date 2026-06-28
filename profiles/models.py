# PROFILES models.py

from django.db import models
from django.contrib.auth.models import User
from PIL import Image, ImageOps
from taggit.managers import TaggableManager

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

    def __str__(self):
        return f"{self.user.username}'s profile"

    @property
    def avatar_url(self):
        if self.image:
            return self.image.url
        return "/static/img/default_profile.png"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Only process if an actual uploaded file exists
        if self.image and hasattr(self.image, "path"):
            try:
                img = Image.open(self.image.path)
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
                img.save(self.image.path)

            except FileNotFoundError:
                pass

