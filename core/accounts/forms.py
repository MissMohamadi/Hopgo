from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm ,PasswordResetForm
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from aio_offline_captcha.form.fields import OfflineCaptchaField
from aio_offline_captcha.form.widgets import OfflineCaptchaWidget
from django import forms
import re

from .utils import normalize_phone_number
from .validators import validate_iranian_national_id, normalize_national_id


User = get_user_model()


class SignUpForm(UserCreationForm):
    captcha = OfflineCaptchaField(widget=OfflineCaptchaWidget())
    error_messages = {
            'password_too_common': 'پسورد بسیار سطحیست لطفا پسورد بهتری ایجاد نمایید',
            "password_mismatch": "عدم تطابق پسورد ها",
        }

    national_id = forms.CharField(
    label="کد ملی",
    max_length=10,
    validators=[validate_iranian_national_id],

    widget=forms.TextInput(
    attrs={
                "placeholder": "کد ملی 10 رقمی",
                "dir": "ltr",
                "inputmode": "numeric",
            }
        )
    )

    class Meta:
        model = User
        fields = ('national_id', 'password1', 'password2', )
        
    

    def __init__(self, *args, **kwargs):
        self.request = kwargs.get('request')
        super(SignUpForm, self).__init__(*args, **kwargs)

    def save(self):
        user_obj = User.objects.create_user(
            national_id=self.cleaned_data["national_id"],
            password=self.cleaned_data["password1"],
        )
        # self.send_mail(user_obj)
        return user_obj
        
        
    def send_mail(self, user):
        from django.contrib.sites.shortcuts import get_current_site
        current_site = get_current_site(self.request)
        mail_subject = 'Activate your account.'
        message = render_to_string('accounts/emails/verification_template.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })
        email = EmailMessage(mail_subject, message, to=[user.email])
        email.send()

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('ایمیل ثبت شده قبلا ثبت نام کرده است.')
        return email
    
    def clean_national_id(self):
        national_id = self.cleaned_data.get("national_id")
        
        if national_id:
            # نرمال‌سازی
            national_id = normalize_national_id(national_id)
            
            # چک یکتایی در دیتابیس
            if User.objects.filter(national_id=national_id).exists():
                raise ValidationError("این کد ملی قبلاً ثبت شده است.")
        
        return national_id


class LoginForm(AuthenticationForm):

    captcha = OfflineCaptchaField(widget=OfflineCaptchaWidget())
    error_messages = {
        'invalid_login':
            "لطفا کد ملی و پسورد صحیح را وارد نمایید",
        'inactive': "This account is inactive."
    }

    # def confirm_login_allowed(self, user):
    #     super(LoginForm, self).confirm_login_allowed(user)

    #     if not user.is_verified:
    #         raise ValidationError(
    #             "User is not verified yet, please follow the instructions for verification",
    #             code='not verified',
    #         )
        # if user.is_superuser:
        #     raise ValidationError(
        #         "User is not verified yet, please follow the instructions for verification",
        #         code='not verified',
        #     )
            
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="کد ملی",
        max_length=10,
        widget=forms.TextInput(
            attrs={
                "placeholder": "کد ملی خود را وارد کنید",
                "dir": "ltr",
                "inputmode": "numeric",
                "autocomplete": "off",
                "autofocus": True,
            }
        )
    )

    captcha = OfflineCaptchaField(widget=OfflineCaptchaWidget())

    error_messages = {
        'invalid_login': "لطفاً کد ملی و رمز عبور صحیح را وارد نمایید.",
        'inactive': "حساب کاربری شما غیرفعال است.",
    }

    def clean_username(self):
        username = self.cleaned_data.get("username")

        if username:
            username = username.strip()
            username = username.translate(
                str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
            )
            username = username.replace(" ", "")
            username = username.replace("-", "")

        return username

    # def confirm_login_allowed(self, user):
    #     super().confirm_login_allowed(user)

        if not user.is_verified:
            raise ValidationError(
                "حساب کاربری شما هنوز تایید نشده است.",
                code="not_verified",
            )

class ForgottenPasswordForm(PasswordResetForm):
    captcha = OfflineCaptchaField(widget=OfflineCaptchaWidget())

# accounts/forms.py
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailLookupForm(forms.Form):
    email = forms.EmailField(
        label="ایمیل",
        widget=forms.EmailInput(attrs={
            'class': 'form-control border-0 bg-light rounded-end ps-1',
            'placeholder': '***@gmail.com'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError("هیچ حساب کاربری فعالی با این ایمیل یافت نشد.")
        return email


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