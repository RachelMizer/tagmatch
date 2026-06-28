# matches > views

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Count

@login_required
def matches_view(request):
    user = request.user
    user_tags = user.profile.tags.all()

    matches = (
        User.objects
        .filter(profile__tags__in=user_tags)
        .exclude(id=user.id)
        .annotate(shared_count=Count("profile__tags"))
        .order_by("-shared_count")
        .distinct()
    )

    for match in matches:
        match.shared_tags = match.profile.tags.filter(id__in=user_tags)

    return render(request, "matches.html", {
        "matches": matches,
    })

