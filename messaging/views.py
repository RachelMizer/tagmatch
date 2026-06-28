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
    # get latest message per sender
    latest_messages = (
        Message.objects
        .filter(recipient=request.user)
        .values("sender")
        .annotate(latest_sent=Max("sent_at"))
        .order_by("-latest_sent")
    )

    # Conver into actual message objects
    messages = Message.objects.filter(
        sender__in=[item["sender"] for item in latest_messages],
        sent_at__in=[item["latest_sent"] for item in latest_messages]
    ).order_by("-sent_at")

    return render(request, "messages/inbox.html", {
        "messages": messages
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

            # Redirect directly to the conversation thread
            return redirect("messages:conversation", username=msg.recipient.username)

    else:
        form = ComposeForm()

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

    return render(request, "messages/conversation.html", {
        "thread": thread,
        "other_user": other_user,
        "form": form,
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
