# messaging/forms.py

from django import forms
from .models import Message
from django.contrib.auth.models import User

class ComposeForm(forms.ModelForm):
    recipient = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="To"
    )

    class Meta:
        model = Message
        fields = ["recipient", "subject", "body"]


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 3})
        }
