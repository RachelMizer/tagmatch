# messaging > context_processors

from .models import Message

def unread_message_count(request):
    if request.user.is_authenticated:
        count = Message.objects.filter(
            recipient=request.user,
            read=False
        ).count()
    else:
        count = 0

    return {"unread_message_count": count}
