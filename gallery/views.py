# gallery > views

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import GalleryImage
from .forms import GalleryImageForm


@login_required
def gallery_view(request):
    images = GalleryImage.objects.filter(user=request.user)

    if request.method == "POST":
        form = GalleryImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.user = request.user
            image.save()
            return redirect("gallery")
    else:
        form = GalleryImageForm()

    return render(request, "gallery.html", {
        "form": form,
        "images": images,
    })


@login_required
def delete_image(request, image_id):
    image = get_object_or_404(GalleryImage, id=image_id, user=request.user)

    if request.method == "POST":
        image.delete()
        return redirect("gallery")

    return redirect("gallery")
