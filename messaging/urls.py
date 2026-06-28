# messaging/urls

from django.urls import path
from . import views

app_name = "messages"

urlpatterns = [
    # Inbox — list of most recent messages
    path("", views.inbox, name="inbox"),

    # Compose — start a new conversation
    path("compose/", views.compose, name="compose"),

    # Conversation thread between two users
    path("conversation/<str:username>/", views.conversation_view, name="conversation"),

    # Delete message link
    path("delete/<int:message_id>/", views.delete_message, name="delete"),

]