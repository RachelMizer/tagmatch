# PROFILES views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegistrationForm

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto-login after registration
            return redirect("home")  # replace with your homepage route
    else:
        form = RegistrationForm()
    return render(request, "profiles/register.html", {"form": form})
