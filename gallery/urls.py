# gallery > urls

from django.urls import path
from . import views

urlpatterns = [
    path("", views.gallery_view, name="gallery"),
    path("delete/<int:image_id>/", views.delete_image, name="delete_image"),
]

