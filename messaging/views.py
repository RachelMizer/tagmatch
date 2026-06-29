# messaging/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Message
from .forms import ComposeForm
from django.db.models import Max
from django.contrib import messages as flash
from django.db.models import Q
from .forms import ReplyForm


@login_required
def inbox(request):
    user = request.user

    # All messages involving the user, newest first
    all_messages = Message.objects.filter(
        Q(sender=user) | Q(recipient=user)
    ).order_by('-sent_at').select_related('sender', 'recipient')

    # One entry per conversation partner — whichever message is most recent
    seen = set()
    conversations = []
    for msg in all_messages:
        partner = msg.recipient if msg.sender == user else msg.sender
        if partner.id not in seen:
            seen.add(partner.id)
            msg.partner = partner
            conversations.append(msg)

    return render(request, "messages/inbox.html", {
        "messages": conversations
    })

# compose — start a brand new conversation
@login_required
def compose(request):
    if request.method == "POST":
        form = ComposeForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.sent_at = timezone.now()
            msg.save()
            return redirect("messages:conversation", username=msg.recipient.username)
    else:
        initial = {}
        to_username = request.GET.get("to")
        if to_username:
            try:
                initial["recipient"] = User.objects.get(username=to_username)
            except User.DoesNotExist:
                pass
        form = ComposeForm(initial=initial)

    return render(request, "messages/compose.html", {
        "form": form
    })


# conversation — full thread + reply box
@login_required
def conversation_view(request, username):
    other_user = get_object_or_404(User, username=username)

    # Get full thread
    thread = Message.objects.filter(
        Q(sender=request.user, recipient=other_user) |
        Q(sender=other_user, recipient=request.user)
    ).order_by("sent_at")

    # Mark received messages as read
    thread.filter(recipient=request.user, read=False).update(read=True)

    # ✅ Use ReplyForm here
    if request.method == "POST":
        form = ReplyForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.recipient = other_user   # ✅ automatically set
            msg.save()
            return redirect("messages:conversation", username=other_user.username)
    else:
        form = ReplyForm()

    time_fmt = "M d, g:i A" if request.user.profile.time_format == "12hr" else "M d, H:i"

    return render(request, "messages/conversation.html", {
        "thread": thread,
        "other_user": other_user,
        "form": form,
        "time_fmt": time_fmt,
    })


@login_required
def delete_message(request, message_id):
    msg = get_object_or_404(Message, id=message_id)

    # ✅ Only allow the sender to delete their own message
    if msg.sender != request.user:
        return HttpResponseForbidden("You can only delete messages you sent.")

    # Determine the other user so we can redirect back to the conversation
    other_user = msg.recipient

    msg.delete()

    return redirect("messages:conversation", username=other_user.username)
