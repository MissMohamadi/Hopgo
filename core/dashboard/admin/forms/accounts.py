from django import forms
from ckeditor.widgets import CKEditorWidget
from dateutil import parser
from jdatetime import datetime as jdatetime
from django.utils.text import slugify
from django.contrib.auth import get_user_model

User = get_user_model()

BOOLEAN_CHOICES = [
    (True, "بله"),
    (False, "خیر"),
]


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email", "type", "is_active", "is_verified"]
        widgets = {
            "email": forms.TextInput(attrs={"class": "form-control"}),
            "type": forms.Select(attrs={"class": "form-select"}),
            "is_active": forms.Select(choices=BOOLEAN_CHOICES, attrs={"class": "form-select"}),
            "is_verified": forms.Select(choices=BOOLEAN_CHOICES, attrs={"class": "form-select"}),
        }


class UserResetPasswordForm(forms.Form):
    new_password = forms.CharField(
    label="رمز عبور جدید",
    min_length=8,
    widget=forms.PasswordInput(
        attrs={
            "class": "form-control",
            "placeholder": "enter the new password",
            "dir": "ltr",
            "style": "text-align: left;",
        }
    ),
)

