from django.shortcuts import render

from django.utils import timezone  # imports and activates the timezone functions

def profile_view(request):
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        tz = request.user.profile.timezone
        timezone.activate(tz)
    else:
        timezone.deactivate()

def login(request):
    return render(request, "login.html")

def landing(request):
    return render(request, "landing.html")

def home(request):
    return render(request, "home.html")

def gallery(request):
    return render(request, "gallery.html")

def matches(request):
    return render(request, "matches.html")

def messages(request):
    return render(request, "messages.html")

def profile(request):
    return render(request, "profile.html")

