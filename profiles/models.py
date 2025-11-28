# PROFILES models.py

from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager # type: ignore

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    timezone = models.CharField(max_length=50, default="UTC")
    image = models.ImageField(upload_to="profiles/", blank=True, null=True)
    tags = TaggableManager(blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

