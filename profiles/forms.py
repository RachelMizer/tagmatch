# PROFILES forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Profile, Report

RELATIONSHIP_CHOICES = [
    ("friendship", "Friendship"),
    ("casual_dating", "Casual Dating"),
    ("long_term", "Long-term"),
    ("ethical_non_mon", "Ethical Non-Monogamous"),
    ("fwb", "Friends with Benefits"),
]

class RegistrationForm(forms.ModelForm):
    # User fields
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    # Profile fields
    location = forms.CharField(max_length=100, required=False)
    gender_identity = forms.CharField(max_length=50, required=False)
    sexuality = forms.CharField(max_length=50, required=False)
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"})
    )
    height_feet = forms.IntegerField(required=False, label="Height (feet)")
    height_inches = forms.IntegerField(required=False, label="Height (inches)")
    build = forms.CharField(max_length=50, required=False)
    relationship_types_seeking = forms.MultipleChoiceField(
        choices=RELATIONSHIP_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    children_status = forms.CharField(max_length=50, required=False)
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class ProfileForm(forms.ModelForm):
    relationship_types_seeking = forms.MultipleChoiceField(
        choices=RELATIONSHIP_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(format='%m-%d-%Y', attrs={"placeholder": "MM-DD-YYYY"}),
        input_formats=['%m-%d-%Y', '%Y-%m-%d'],
    )

    class Meta:
        model = Profile
        fields = [
            "location",
            "gender_identity",
            "sexuality",
            "date_of_birth",
            "height_feet",
            "height_inches",
            "build",
            "relationship_types_seeking",
            "children_status",
            "image",
            "time_format",
        ]


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Please describe what happened...'}),
        }
