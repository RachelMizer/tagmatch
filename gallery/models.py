# gallery > models

from django.db import models
from django.contrib.auth.models import User

class GalleryImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ImageField(upload_to="gallery/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
