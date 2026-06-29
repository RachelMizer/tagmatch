# PROFILES > views
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from .forms import RegistrationForm, ProfileForm, ReportForm
from .models import Profile, Block, Report
from django.shortcuts import get_object_or_404
from gallery.models import GalleryImage
from taggit.models import Tag
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.signing import TimestampSigner, BadSignature
from django.core.mail import send_mail
from django.conf import settings as django_settings

# dictionary for relationship type labels
RELATIONSHIP_LABELS = {
    'friendship': 'Friendship',
    'fwb': 'Friends with Benefits',
    'casual_dating': 'Casual Dating',
    'long_term': 'Long-term',
    'ethical_non_mon': 'Ethical Non-Monogamous',
}

def _send_verification_email(user, request):
    signer = TimestampSigner()
    token = signer.sign(user.pk)
    verify_url = request.build_absolute_uri(f"/profiles/verify-email/{token}/")
    send_mail(
        subject="Verify your TagMatch email address",
        message=f"Hi {user.first_name or user.username},\n\nPlease verify your email address by clicking the link below:\n\n{verify_url}\n\nThis link expires in 24 hours.\n\n— The TagMatch Team",
        from_email=django_settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.email = form.cleaned_data["email"]
            user.set_password(form.cleaned_data["password"])
            user.save()

            Profile.objects.create(
                user=user,
                location=form.cleaned_data.get("location"),
                gender_identity=form.cleaned_data.get("gender_identity"),
                sexuality=form.cleaned_data.get("sexuality"),
                date_of_birth=form.cleaned_data.get("date_of_birth"),
                height_feet=form.cleaned_data.get("height_feet"),
                height_inches=form.cleaned_data.get("height_inches"),
                build=form.cleaned_data.get("build"),
                relationship_types_seeking=form.cleaned_data.get("relationship_types_seeking"),
                children_status=form.cleaned_data.get("children_status"),
                image=form.cleaned_data.get("profile_image"),
            )

            _send_verification_email(user, request)
            auth_login(request, user)
            return redirect("home")
    else:
        form = RegistrationForm()

    return render(request, "register.html", {"form": form})


def verify_email(request, token):
    signer = TimestampSigner()
    try:
        user_pk = signer.unsign(token, max_age=86400)
        user = User.objects.get(pk=user_pk)
        user.profile.email_verified = True
        user.profile.save(update_fields=["email_verified"])
        return render(request, "verify_email_done.html", {"success": True})
    except (BadSignature, User.DoesNotExist):
        return render(request, "verify_email_done.html", {"success": False})


@login_required
def resend_verification(request):
    if not request.user.profile.email_verified:
        _send_verification_email(request.user, request)
        messages.success(request, "Verification email sent. Check your inbox.")
    return redirect("my_profile")


@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("edit_profile")  # or "profile_self" if you want to redirect to the profile page
    else:
        form = ProfileForm(instance=profile)

    all_tags = Tag.objects.all()
    user_tags = profile.tags.all()

    return render(request, "edit_profile.html", {
        "form": form,
        "all_tags": all_tags,
        "user_tags": user_tags,
    })




@login_required
def update_tags(request):
    if request.method == "POST":
        profile = request.user.profile
        tag_id = request.POST.get("tag_id")

        if tag_id:
            tag = get_object_or_404(Tag, id=tag_id)
            tag_name = tag.name

            if tag_name in profile.tags.names():
                profile.tags.remove(tag_name)
            else:
                profile.tags.add(tag_name)

    return redirect("edit_profile")


@login_required
def profile(request):
    profile = request.user.profile
    user_tags = profile.tags.all()

    return render(request, "profile.html", {
        "profile": profile,
        "user_tags": user_tags,
        "relationship_labels": RELATIONSHIP_LABELS,
    })



# Profile View
def profile_view(request, username):
    target_user = get_object_or_404(User, username=username)
    try:
        profile = target_user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=target_user)

    user_tags = profile.tags.all()

    return render(request, "profiles/profile_view.html", {
        "profile": profile,
        "user_tags": user_tags,
        "relationship_labels": RELATIONSHIP_LABELS,
    })


@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        auth_logout(request)
        user.delete()
        return redirect("landing")
    return render(request, "delete_account.html")


@login_required
def block_user(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return redirect("profile")
    already_blocked = Block.objects.filter(blocker=request.user, blocked=target).exists()
    return render(request, "block_confirm.html", {
        "target": target,
        "already_blocked": already_blocked,
    })


@login_required
def confirm_block(request, username):
    if request.method == "POST":
        target = get_object_or_404(User, username=username)
        if target != request.user:
            Block.objects.get_or_create(blocker=request.user, blocked=target)
        return render(request, "block_done.html", {"target": target})
    return redirect("block_user", username=username)


@login_required
def unblock_user(request, username):
    if request.method == "POST":
        target = get_object_or_404(User, username=username)
        Block.objects.filter(blocker=request.user, blocked=target).delete()
    return redirect("blocked_reported")


@login_required
def report_user(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return redirect("profile")
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.reported = target
            report.save()
            return render(request, "report_done.html", {"target": target})
    else:
        form = ReportForm()
    return render(request, "report_user.html", {"form": form, "target": target})


@login_required
def blocked_reported(request):
    blocked_users = Block.objects.filter(blocker=request.user).select_related('blocked')
    reports_made = Report.objects.filter(reporter=request.user).select_related('reported').order_by('-created_at')
    return render(request, "blocked_reported.html", {
        "blocked_users": blocked_users,
        "reports_made": reports_made,
    })


# Gallery views
def gallery_view(request, username):
    user = get_object_or_404(User, username=username)
    images = GalleryImage.objects.filter(user=user)

    return render(request, "profiles/gallery_view.html", {
        "user": user,
        "images": images,
    })
