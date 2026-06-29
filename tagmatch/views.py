# tagmatch/views.py

from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from datetime import timedelta
from messaging.models import Message
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.core.paginator import Paginator
from taggit.models import Tag
from profiles.models import Block



# ---------------------------------------------------------
# Authentication
# ---------------------------------------------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


# ---------------------------------------------------------
# Landing + Home (Dashboard)
# ---------------------------------------------------------
def landing(request):
    if request.user.is_authenticated:
        return redirect("home")
    return render(request, "landing.html")



@login_required
def home(request):
    user = request.user
    user_tags = user.profile.tags.all()

    blocked_ids = Block.objects.filter(blocker=user).values_list('blocked_id', flat=True)
    blocking_ids = Block.objects.filter(blocked=user).values_list('blocker_id', flat=True)
    excluded_ids = set(blocked_ids) | set(blocking_ids)

    latest_matches = (
        User.objects
        .filter(profile__tags__in=user_tags)
        .exclude(id=user.id)
        .exclude(id__in=excluded_ids)
        .annotate(shared_count=Count("profile__tags"))
        .order_by("-shared_count")
        .distinct()[:5]
    )

    latest_messages = Message.objects.filter(
        recipient=user
    ).order_by('-sent_at')[:5]

    one_week_ago = timezone.now() - timedelta(days=7)
    new_members = User.objects.filter(
        date_joined__gte=one_week_ago
    ).exclude(id__in=excluded_ids).order_by("-date_joined")

    no_tags = user.profile.tags.count() == 0

    context = {
        "latest_matches": latest_matches,
        "latest_messages": latest_messages,
        "new_members": new_members,
        "no_tags": no_tags,
    }

    return render(request, "home.html", context)

# ---------------------------------------------------------
# User Dashboard Pages
# ---------------------------------------------------------
@login_required
def gallery(request):
    return render(request, "gallery.html")


@login_required
def gallery_view(request):
    return render(request, "gallery_view.html")


# ---------------------------------------------------------
# Matches View
# ---------------------------------------------------------
@login_required
def matches_view(request):
    user = request.user
    user_tags = user.profile.tags.all()

    blocked_ids = Block.objects.filter(blocker=user).values_list('blocked_id', flat=True)
    blocking_ids = Block.objects.filter(blocked=user).values_list('blocker_id', flat=True)
    excluded_ids = set(blocked_ids) | set(blocking_ids)

    matches_qs = (
        User.objects
        .filter(profile__tags__in=user_tags)
        .exclude(id=user.id)
        .exclude(id__in=excluded_ids)
        .annotate(shared_count=Count("profile__tags"))
        .order_by("-shared_count")
        .distinct()
    )

    paginator = Paginator(matches_qs, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    for match in page_obj:
        match.shared_tags = match.profile.tags.filter(id__in=user_tags)

    return render(request, "matches.html", {
        "matches": page_obj,
        "page_obj": page_obj,
    })


# ---------------------------------------------------------
# Messages
# ---------------------------------------------------------
@login_required
def user_messages(request):
    return render(request, "messages/inbox.html")


# ---------------------------------------------------------
# Search View
# ---------------------------------------------------------
@login_required
def search_view(request):
    all_tags = Tag.objects.all().order_by("name")
    selected_tag_ids = request.GET.getlist("tags")

    user = request.user
    blocked_ids = Block.objects.filter(blocker=user).values_list('blocked_id', flat=True)
    blocking_ids = Block.objects.filter(blocked=user).values_list('blocker_id', flat=True)
    excluded_ids = set(blocked_ids) | set(blocking_ids)

    users_qs = User.objects.exclude(id=user.id).exclude(id__in=excluded_ids)

    if selected_tag_ids:
        users_qs = users_qs.filter(profile__tags__id__in=selected_tag_ids).distinct()

    paginator = Paginator(users_qs, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "search.html", {
        "all_tags": all_tags,
        "selected_tag_ids": list(map(int, selected_tag_ids)),
        "users": page_obj,
        "page_obj": page_obj,
    })


# ---------------------------------------------------------
# Dev Pages
# ---------------------------------------------------------
def devnotes(request):
    return render(request, "devnotes.html")


def sitemap(request):
    return render(request, "sitemap.html")
