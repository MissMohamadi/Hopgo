from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm ,PasswordResetForm
from django.core.exceptions import ValidationError
from aio_offline_captcha.form.fields import OfflineCaptchaField
from aio_offline_captcha.form.widgets import OfflineCaptchaWidget
from django.contrib.auth.forms import SetPasswordForm
from django import forms
import re
from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from .utils import normalize_phone_number

User = get_user_model()

class PersianPasswordErrorsMixin:
    """mixin مشترک برای فارسی‌سازی خطاهای ولیدیتورهای رمز عبور"""
    password_error_messages = {
        "password_too_similar": _("رمز عبور شما مشابه اطلاعات شخصی شماست."),
        "password_too_short": _("رمز عبور باید حداقل 8 نویسه باشد."),
        "password_too_common": _("این رمز عبور بسیار رایج است؛ لطفاً رمز قوی‌تری انتخاب کنید."),
        "password_entirely_numeric": _("رمز عبور نمی‌تواند کاملاً عددی باشد."),
    }

    def validate_password_fa(self, password, user=None):
        try:
            password_validation.validate_password(password, user)
        except ValidationError as exc:
            translated = []
            for error in exc.error_list:
                code = getattr(error, "code", None)
                if code in self.password_error_messages:
                    translated.append(
                        ValidationError(
                            self.password_error_messages[code],
                            code=code,
                            params=getattr(error, "params", None),
                        )
                    )
                else:
                    translated.append(error)
            raise ValidationError(translated)

class SignUpForm(PersianPasswordErrorsMixin, UserCreationForm):
    error_messages = {
        "password_mismatch": _("رمز عبور و تکرار آن با هم همخوانی ندارند."),
    }
    captcha = OfflineCaptchaField(widget=OfflineCaptchaWidget())

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise ValidationError("این نام کاربری قبلاً ثبت شده است.", code="duplicate")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("این ایمیل قبلاً ثبت شده است.", code="duplicate")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(self.error_messages["password_mismatch"], code="password_mismatch")
        self.validate_password_fa(password2, self.instance)
        return password2

class LoginForm(AuthenticationForm):
    captcha = OfflineCaptchaField(widget=OfflineCaptchaWidget())
    error_messages = {
        'invalid_login': "نام کاربری یا رمز عبور صحیح نیست.",
        'inactive': "حساب کاربری شما غیرفعال است.",
    }
    # نیازی به override کردن فیلد username نیست مگر برای استایل خاص
class ForgottenPasswordForm(PasswordResetForm):
    captcha = OfflineCaptchaField(widget=OfflineCaptchaWidget())

class ResetPasswordForm(PersianPasswordErrorsMixin, SetPasswordForm):
    error_messages = {
        "password_mismatch": _("رمز عبور جدید و تکرار آن با هم همخوانی ندارند."),
    }

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )

        self.validate_password_fa(password2, self.user)
        return password2

class SendOtpForm(forms.Form):
    phone = forms.CharField(
        max_length=25,
        required=True,
        label="شماره موبایل",
        widget=forms.TextInput(
            attrs={
                "class": "block w-full rounded-md border-gray-300 p-3",
                "placeholder": "09123456789",
                "dir": "ltr",
                "autocomplete": "tel",
            }
        ),
    )

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        phone = normalize_phone_number(phone)

        if not re.match(r"^09\d{9}$", phone):
            raise ValidationError("شماره موبایل معتبر نیست.")

        return phone