# PROFILES forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Profile, Report
from datetime import date

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
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    # Profile fields
    location = forms.CharField(max_length=100, required=False)
    gender_identity = forms.CharField(max_length=50, required=False)
    sexuality = forms.CharField(max_length=50, required=False)
    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Date of Birth",
        help_text="You must be 18 or older to register.",
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
    agree_to_tos = forms.BooleanField(
        required=True,
        label="I agree to the Terms of Service and Privacy Policy",
        error_messages={"required": "You must agree to the Terms of Service and Privacy Policy to register."},
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password"]

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get("date_of_birth")
        if dob:
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 18:
                raise forms.ValidationError("You must be at least 18 years old to register.")
        return dob

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
