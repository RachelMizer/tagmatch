# gallery > forms

from django import forms
from .models import GalleryImage

class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ["file"]
        labels = {"file": "Upload Image"}
