from django.contrib.auth.forms import AuthenticationForm
from django.forms.models import BaseModelForm
from django.views import generic
from django.views.generic import base
from django.contrib.auth import views
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect,render
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import get_user_model
from ..forms import SignUpForm, LoginForm ,ForgottenPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from ..forms import EmailLookupForm
import logging

from django.core.cache import cache
from django.contrib.auth import login as auth_login

from django.utils.crypto import get_random_string

from ..forms import SendOtpForm
from ..services import send_sms_ir_otp

logger = logging.getLogger(__name__)

User = get_user_model()

class RegistrationView(generic.CreateView):
    template_name = 'accounts/signup.html'
    form_class = SignUpForm
    redirect_authenticated_user = True
    success_url = reverse_lazy("accounts:login")
    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and request.user.is_authenticated:
            return HttpResponseRedirect('/')
        return super().dispatch(request, *args, **kwargs)
    
    print('2')
    def form_valid(self, form):
        # ذخیره کاربر و دسترسی به آبجکت ساخته‌شده
        self.object = form.save()
        print('3')
        # پیام موفقیت با کد ملی ماسک‌شده
        messages.success(
            self.request,
            f'{self.object.masked_national_id} عزیز، ثبت نام شما با موفقیت انجام شد. حال می‌توانید وارد شوید.'
        )
        
        
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        # نمایش خطاها با messages
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{error}")
                print(f"error:{error}")
            print('4')
        return redirect(reverse_lazy("accounts:signup"))
    
class LoginView(views.LoginView):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form: AuthenticationForm):
        user = form.get_user()
        
        # لاگ ماسک‌شده
        print("✅ [DEBUG] لاگین موفق!")
        print(f"👤 national_id: {user.masked_national_id}")
        print(f"🔑 is_staff: {user.is_staff}")
        
        response = super().form_valid(form)
        
        messages.success(
            self.request,
            f'{user.masked_national_id} عزیز، با موفقیت وارد شدید 👋'
        )
        
        if next_url := self.request.GET.get("next"):
            return redirect(next_url)
        
        return response

    def form_invalid(self, form: AuthenticationForm):
        print("❌ [DEBUG] لاگین شکست خورد!")
        
        # فقط کد ملی ماسک‌شده، رمز عبور اصلاً پرینت نشود
        username = form.data.get("username", "")
        if username and len(username) >= 5:
            print(f"👤 national_id: {username[:3]}*****{username[-2:]}")
        
        print(f"⚠️ خطاهای فرم: {form.errors}")
        return super().form_invalid(form)
    
class EmailVerificationSendView(generic.TemplateView):
    template_name = 'accounts/email_verification_send.html'
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        return super().dispatch(request, *args, **kwargs)


# def activate(request, uidb64, token):
#     User = get_user_model()
#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         user = User.objects.get(pk=uid)
#     except(TypeError, ValueError, OverflowError, User.DoesNotExist):
#         user = None
#     if user is not None and account_activation_token.check_token(user, token):
#         user.is_active = True
#         user.save()
#         return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
#     else:
#         return HttpResponse('Activation link is invalid!')

class AccountActivationView(base.TemplateResponseMixin, generic.View):
    template_name = 'accounts/email_verification_check.html'
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        User = get_user_model()
        try:
            uid = force_text(urlsafe_base64_decode(kwargs["uidb64"]))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and default_token_generator.check_token(user, kwargs["token"]):
            user.is_verified = True
            user.save()
            messages.success(request, "verification was successfully done")
            return redirect(reverse("accounts:login"))
        messages.error(request, "failed to verify user please try again")
        return redirect(reverse("accounts:login"))


class LogoutView(views.LogoutView):
    template_name = 'accounts/logged_out.html'


class PasswordChangeView(views.PasswordChangeView):
    template_name = 'accounts/password_change_form.html'


class PasswordChangeDoneView(views.PasswordChangeDoneView):
    template_name = 'accounts/password_change_done.html'


class PasswordResetView(views.PasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/emails/password_reset_email.html'
    success_url = reverse_lazy('accounts:password_reset_done')
    form_class = ForgottenPasswordForm


class PasswordResetDoneView(views.PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class PasswordResetConfirmView(views.PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


class PasswordResetCompleteView(views.PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'




class PasswordResetRequestView(generic.FormView):
    """مرحله اول: دریافت و اعتبارسنجی ایمیل"""
    template_name = 'accounts/password_reset_form.html'
    form_class = EmailLookupForm

    def form_valid(self, form):
        # ذخیره ایمیل در سشن پس از تایید
        self.request.session['reset_email'] = form.cleaned_data['email']
        # ریدایرکت به صفحه تغییر رمز
        return redirect('accounts:password_reset_set')


class PasswordResetSetView(generic.FormView):
    """مرحله دوم: تنظیم رمز عبور جدید"""
    template_name = 'accounts/password_reset_set.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        # اگر ایمیل در سشن نبود، کاربر را به مرحله اول برگردان
        if 'reset_email' not in request.session:
            return redirect('accounts:password_reset')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # SetPasswordForm نیاز به آبجکت user دارد
        try:
            user = User.objects.get(email__iexact=self.request.session['reset_email'])
            kwargs['user'] = user
        except User.DoesNotExist:
            # اگر کاربر پیدا نشد، سشن را پاک کن و برگرد به مرحله اول
            if 'reset_email' in self.request.session:
                del self.request.session['reset_email']
            return redirect('accounts:password_reset')
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'رمز عبور شما با موفقیت تغییر یافت. اکنون می‌توانید وارد شوید.')
        # پاک کردن سشن پس از موفقیت
        if 'reset_email' in self.request.session:
            del self.request.session['reset_email']
        return super().form_valid(form)

import requests
from decouple import config
from django.conf import settings

class SmsIrService:
    BASE_URL = "https://api.sms.ir/v1/send/verify"

    @classmethod
    def send_otp(cls, mobile: str, code: str) -> dict:
        """
        ارسال کد تایید از طریق پنل sms.ir
        """
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/plain', # طبق داکیومنت رسمی sms.ir
            'x-api-key': config("SMS_IR_API_KEY", default="")
        }
        

        payload = {
            "mobile": mobile,
            "templateId": config("SMS_IR_TEMPLATE_ID", cast=int, default=0),
            "parameters": [
                {
                    # نام این فیلد باید دقیقاً با متغیر داخل قالب در پنل sms.ir یکی باشد
                    "name": "Code", 
                    "value": code
                }
            ]
        }

        try:
            response = requests.post(cls.BASE_URL, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            # در پروداکشن حتماً این خطا را در Sentry لاگ کنید
            return {"status": -1, "message": f"خطا در ارتباط با سرویس پیامک: {str(e)}"}    


"""
view for send otp : sms.ir
"""
def send_otp(request):
    if request.method == "POST":
        print('1')
        form = SendOtpForm(request.POST)
        if form.is_valid():
            print('2')
            phone = form.cleaned_data["phone"]
            print(f"phone:{phone}") 
            otp_cache_key = f"otp_{phone}"
            rate_limit_key = f"otp_rate_{phone}"
            # جلوگیری از ارسال رگباری
            if cache.get(rate_limit_key):
                form.add_error(
                    None,
                    "کد تایید به‌تازگی برای این شماره ارسال شده است. لطفاً چند لحظه صبر کنید.",
                )
            else:
                # تولید کد ۵ رقمی
                otp_code = get_random_string(
                    length=5,
                    allowed_chars="123456789",
                )
                print('3')
                # ذخیره کد در کش به مدت ۲ دقیقه
                cache.set(otp_cache_key, otp_code, 120)
                # جلوگیری از درخواست مجدد تا ۱ دقیقه
                cache.set(rate_limit_key, True, 60)
                success, message = send_sms_ir_otp(phone, otp_code)

                if success:

                    # برای استفاده در مرحله تایید کد
                    request.session["otp_phone"] = phone
                    messages.success(
                        request,
                        "کد تایید برای شماره موبایل شما ارسال شد.",
                    )
                    print('4')
                    # اگر صفحه تایید کد داری، اینجا ریدایرکت کن:
                    return redirect("accounts:verify_otp")


                else:
                    print('5')
                    # اگر ارسال ناموفق بود، کش را پاک می‌کنیم تا کاربر بتواند دوباره تلاش کند
                    cache.delete(otp_cache_key)
                    cache.delete(rate_limit_key)

                    logger.error("OTP send failed for %s: %s", phone, message)

                    form.add_error(
                        None,
                        "ارسال کد تایید با مشکل مواجه شد. دوباره تلاش کنید.",
                    )
    else:
        print('6')
        form = SendOtpForm()

    return render(
        request,
        "accounts/send_otp.html",
        {
            "form": form,
        },
    )

"""
view for verify otp : sms.ir
"""
MAX_OTP_ATTEMPTS = 5

def verify_otp(request):
    phone = request.session.get("otp_phone")

    # اگر کاربر بدون درخواست کد، مستقیم وارد این صفحه شد
    if not phone:
        messages.error(request, "ابتدا شماره موبایل خود را وارد کنید.")
        return redirect("accounts:send_otp")

    if request.method == "POST":
        code = request.POST.get("code", "").strip()

        # تبدیل اعداد فارسی به انگلیسی
        code = code.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))

        otp_key = f"otp_{phone}"
        attempts_key = f"otp_attempts_{phone}"

        stored_code = cache.get(otp_key)

        # کد منقضی شده یا وجود ندارد
        if stored_code is None:
            messages.error(request, "کد تایید منقضی شده است. لطفاً دوباره درخواست کد دهید.")
            return redirect("accounts:send_otp")

        # محدودیت تعداد تلاش
        attempts = cache.get(attempts_key, 0)
        if attempts >= MAX_OTP_ATTEMPTS:
            cache.delete(otp_key)
            cache.delete(attempts_key)
            messages.error(request, "تعداد تلاش‌ها تمام شد. لطفاً کد جدید درخواست دهید.")
            return redirect("accounts:send_otp")

        if code == stored_code:
            # موفقیت: کد یک‌بارمصرف است، پس حذفش می‌کنیم
            cache.delete(otp_key)
            cache.delete(attempts_key)
            request.session.pop("otp_phone", None)

            user = User.objects.filter(phone_number=phone).first()

            if user is None:
                # کاربر جدید: شماره تاییدشده را نگه می‌داریم برای تکمیل ثبت‌نام
                request.session["verified_phone"] = phone
                messages.info(request, "شماره موبایل تایید شد؛ لطفاً ثبت‌نام را کامل کنید.")
                return redirect("accounts:signup")

            if not user.is_active:
                messages.error(request, "حساب کاربری شما غیرفعال است.")
                return redirect("accounts:send_otp")

            # اگر چند AUTHENTICATION_BACKENDS تعریف کردی، بک‌اند را صریح بفرست:
            # auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            auth_login(request, user)
            messages.success(request, "ورود با موفقیت انجام شد.")
            return redirect("/")
        else:
            attempts += 1
            cache.set(attempts_key, attempts, 300)
            messages.error(
                request,
                f"کد تایید صحیح نیست. (تلاش {attempts} از {MAX_OTP_ATTEMPTS})"
            )

    return render(request, "accounts/verify_otp.html")