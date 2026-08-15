from django import forms
from accounts.models import ProfileModel
from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

User= get_user_model()


phone_regex = RegexValidator(
    regex=r"^09\d{9}$",
    message="Phone number must be 11 digits long and start with 09 (e.g., 09124610183)."
)
class CustomerProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "نام خود را وارد کنید"})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "نام خانوادگی خود را وارد کنید"})
    )
    phone_number = forms.CharField(
        validators=[phone_regex],
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "09xxxxxxxxx",
            "pattern": "^09\\d{9}$",
            "oninput": "this.value = this.value.replace(/[^0-9]/g, '')",  # Allow only numbers
            "maxlength": "11"
        }),
        required=False
    )

class AdminProfileForm(forms.ModelForm):
    phone_number = forms.CharField(
        validators=[phone_regex],
        widget=forms.TextInput(attrs={
            "class": "form-control force-ltr",
            "placeholder": "09xxxxxxxxx",
            "pattern": "^09\\d{9}$",
            "oninput": "this.value = this.value.replace(/[^0-9]/g, '')",  # Allow only numbers
            "maxlength": "11"
        }),
        required=False
    )
    class Meta:
        model = ProfileModel
        fields = ["first_name", "last_name", "phone_number", "title", "resume_url","bio"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),            
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            "resume_url": forms.URLInput(attrs={"class": "form-control force-ltr"}),
        }



class AdminPasswordChangeForm(forms.Form):
    """
    A form that lets a user change their password by entering their old password.
    """
    error_messages = {
        "password_incorrect": _("رمز قدیمی اشتباه است لطفا مجدد سعی نمایید."),
        "password_mismatch": _("دو پسورد جدید و تایید آن با هم همخوانی ندارند"),
        "password_too_similar": _("پسورد شما مشابه اطلاعات شخصی شماست."),
        "password_common": _("این پسورد بسیار رایج است، لطفا پسورد قوی تری انتخاب کنید."),
        "password_numeric": _("پسورد شما نمی‌تواند فقط عددی باشد."),
    }

    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password", "autofocus": True,"class":"form-control",
                                          "placeholder":"رمز قدیمی خود را وارد کنید"}),
    )
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password","class":"form-control",
                                          "placeholder":"رمز جدید خود را وارد کنید"}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password","class":"form-control","placeholder":"رمز جدید خود را مجدد وارد کنید"}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        """
        Validate that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise ValidationError(
                self.error_messages["password_incorrect"],
                code="password_incorrect",
            )
        return old_password

    def clean_new_password2(self):
        """
        Ensure the new passwords match.
        """
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        password_validation.validate_password(password2, self.user)
        return password2

    def save(self, commit=True):
        """
        Set the new password for the user.
        """
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user

    