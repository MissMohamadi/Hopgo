# accounts/views.py
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import views as auth_views
from django.contrib.auth import login as auth_login
from django.contrib.auth import get_user_model
from django.views import generic
from django.urls import reverse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.cache import cache
import logging

from ..forms import SendOtpForm, SignUpForm, LoginForm, ResetPasswordForm
from ..services import generate_otp_code, send_otp_code
from ..utils import get_user_by_phone, normalize_phone_number
from ..models import UserType

logger = logging.getLogger(__name__)

User = get_user_model()
MAX_OTP_ATTEMPTS = 5


SIGNUP_ROLE_SESSION_KEY = "signup_role"
VALID_SIGNUP_ROLES = ("walker", "owner")


# ============================================================
# انتخاب نقش
# ============================================================


def role_to_user_type(role: str) -> int:
    """
    تبدیل نقش انتخاب شده در Session به مقدار UserType
    طبق مدل جدید: customer=داگ واکر, supervisor=داگ اونر
    """
    if role == "walker":
        return UserType.supervisor.value  # 2 → walker
    return UserType.customer.value 

class RoleSelectView(generic.TemplateView):
    template_name = "accounts/select_role.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("website:index")
        return super().dispatch(request, *args, **kwargs)

    def _save_role_and_redirect(self, request, role):
        if role not in VALID_SIGNUP_ROLES:
            # ✅ کاربر در همین صفحه می‌ماند — بدون ریدایرکت
            messages.error(request, "لطفاً یکی از گزینه‌ها را انتخاب کنید.")
            return None

        request.session[SIGNUP_ROLE_SESSION_KEY] = role
        request.session.modified = True

        #  اگر قبلاً OTP را تایید کرده، مستقیم برود signup
        # if request.session.get('verified_phone'):
        #     return redirect('accounts:signup')
        # # در غیر این صورت برود send_otp
        # return redirect('accounts:send_otp')
        return redirect('accounts:signup')
    
    def get(self, request, *args, **kwargs):
        role = request.GET.get("role")
        if role:
            response = self._save_role_and_redirect(request, role)
            if response:
                return response
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        role = request.POST.get("role")
        response = self._save_role_and_redirect(request, role)
        if response:
            return response
        # ✅ نقش نامعتبر بود → کاربر در همین صفحه می‌ماند
        return self.render_to_response(self.get_context_data())
    
# ============================================================
# ثبت‌نام و ورود
# ============================================================

class RegistrationView(generic.CreateView):
    template_name = 'accounts/signup.html'
    form_class = SignUpForm
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and request.user.is_authenticated:
            return HttpResponseRedirect(reverse('website:index'))

        # verify phone number
        # if not request.session.get('verified_phone'):
        #     messages.error(request, 'ابتدا شماره موبایل خود را تایید کنید.')
        #     return redirect('accounts:send_otp')

        #  چک نقش فقط اینجا
        self.signup_role = request.session.get(SIGNUP_ROLE_SESSION_KEY)
        if self.signup_role not in VALID_SIGNUP_ROLES:
            # بدون پیام خطا — ساکت بفرست به انتخاب نقش
            return redirect('accounts:select_role')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        verified_phone = self.request.session.get('verified_phone')

        self.object = form.save(commit=False)
        self.object.phone_number = verified_phone
        self.object.type = role_to_user_type(self.signup_role)
        self.object.save()

        self.request.session.pop('verified_phone', None)
        self.request.session.pop(SIGNUP_ROLE_SESSION_KEY, None)

        auth_login(
            self.request,
            self.object,
            backend="django.contrib.auth.backends.ModelBackend",
        )

        messages.success(
            self.request,
            f'{self.object.username} عزیز، ثبت‌نام کامل شد؛ خوش آمدید! 👋'
        )
        return redirect(reverse('website:index'))

    def form_invalid(self, form):
        logger.warning("Signup invalid: %s", form.errors)
        return self.render_to_response(self.get_context_data(form=form))

    
class LoginView(auth_views.LoginView):
    """ورود با نام کاربری و رمز عبور"""
    template_name = 'accounts/login.html'
    form_class = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form: AuthenticationForm):
        user = form.get_user()
        response = super().form_valid(form)
        messages.success(self.request, f'{user.username} عزیز، با موفقیت وارد شدید 👋')

        if next_url := self.request.GET.get("next"):
            return redirect(next_url)

        user_role = getattr(user, 'type', None)
        print(f"user_role:{user_role} ")

        if user_role == 2:
            return redirect('DogWalker:index')  # نام URL صفحه واکر
        elif user_role == 1 :
            return redirect('DogOwner:index')   # نام URL صفحه اونر

            
        # در صورتی که نقش مشخص نبود یا مقادیر دیگری داشت (ریدایرکت پیش‌فرض)
        return response

    def form_invalid(self, form: AuthenticationForm):
        logger.warning("Login invalid: %s", form.errors)
        return super().form_invalid(form)

class LogoutView(auth_views.LogoutView):
    template_name = 'accounts/logged_out.html'

# ============================================================
# ارسال OTP (مرحله اول)
# ============================================================
class BaseOtpView(generic.FormView):
    """کلاس پایه برای ارسال OTP - منطق مشترک بین ثبت‌نام و بازیابی رمز"""
    template_name = None
    form_class = SendOtpForm
    otp_ttl = 120          
    rate_limit_ttl = 60   

    def get_otp_cache_key(self, phone):
        return f"otp_{phone}"

    def get_rate_limit_key(self, phone):
        return f"otp_rate_{phone}"

    def get_session_key(self):
        raise NotImplementedError("Subclass باید get_session_key را override کند.")

    def get_success_message(self):
        return "کد تایید برای شماره موبایل شما ارسال شد."

    def get_success_url(self):
        raise NotImplementedError("Subclass باید get_success_url را override کند.")

    def pre_send_validation(self, form):
        return True

    def form_valid(self, form):
        phone = form.cleaned_data["phone"]

        if not self.pre_send_validation(form):
            return self.form_invalid(form)

        otp_cache_key = self.get_otp_cache_key(phone)
        rate_limit_key = self.get_rate_limit_key(phone)

        if cache.get(rate_limit_key):
            form.add_error(
                None,
                "کد تایید به‌تازگی برای این شماره ارسال شده است. لطفاً چند لحظه صبر کنید.",
            )
            return self.form_invalid(form)

        otp_code = generate_otp_code()

        cache.set(otp_cache_key, otp_code, self.otp_ttl)
        cache.set(rate_limit_key, True, self.rate_limit_ttl)

        success, message = send_otp_code(phone, otp_code)

        if success:
            self.request.session[self.get_session_key()] = phone
            messages.success(self.request, self.get_success_message())
            return redirect(self.get_success_url())

        cache.delete(otp_cache_key)
        cache.delete(rate_limit_key)
        logger.error(
            "OTP send failed for phone (masked): %s - %s",
            phone[:4] + "****" + phone[-4:] if len(phone) >= 8 else "***",
            message,
        )
        form.add_error(None, f"ارسال کد تایید با مشکل مواجه شد: {message}")
        return self.form_invalid(form)


class SendOtpView(BaseOtpView):
    """ارسال OTP برای ورود/ثبت‌نام"""
    template_name = 'accounts/send_otp.html'

    def get_session_key(self):
        return "otp_phone"

    def get_success_url(self):
        return reverse('accounts:verify_otp')

    def get_success_message(self):
        return "کد تایید برای شماره موبایل شما ارسال شد."


class SendResetOtpView(BaseOtpView):
    """ارسال OTP برای بازیابی رمز عبور"""
    template_name = 'accounts/password_reset_request.html'

    def pre_send_validation(self, form):
        phone = form.cleaned_data["phone"]
        user = get_user_by_phone(phone)

        if not user:
            form.add_error('phone', 'کاربری با این شماره موبایل در سیستم ثبت نشده است.')
            return False
        return True

    def get_session_key(self):
        return "reset_phone"

    def get_success_url(self):
        return reverse('accounts:verify_reset_otp')

    def get_success_message(self):
        return "کد تایید برای بازیابی رمز عبور به شماره موبایل شما ارسال شد."


# ============================================================
# تایید OTP (مرحله دوم)
# ============================================================
class BaseVerifyOtpView(generic.TemplateView):
    """کلاس پایه برای تایید کد OTP"""
    max_attempts = MAX_OTP_ATTEMPTS
    attempts_ttl = 120  

    phone_session_key = None
    attempts_cache_prefix = None
    redirect_on_missing = None

    def get_otp_cache_key(self, phone):
        return f"otp_{phone}"

    def get_attempts_cache_key(self, phone):
        return f"{self.attempts_cache_prefix}_{phone}"

    def dispatch(self, request, *args, **kwargs):
        phone = request.session.get(self.phone_session_key)
        if not phone:
            messages.error(request, 'ابتدا شماره موبایل خود را وارد کنید.')
            return redirect(self.redirect_on_missing)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        phone = self.request.session.get(self.phone_session_key)
        attempts = cache.get(self.get_attempts_cache_key(phone), 0)
        context['attempts'] = attempts
        context['max_attempts'] = self.max_attempts
        context['masked_phone'] = (
            f"{phone[:4]}****{phone[-4:]}" if phone and len(phone) >= 8 else None
        )
        return context

    def on_success(self, request, phone):
        raise NotImplementedError("Subclass باید on_success را override کند.")

    def post(self, request, *args, **kwargs):
        phone = request.session.get(self.phone_session_key)
        code = request.POST.get('code', '').strip()
        code = code.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))

        otp_key = self.get_otp_cache_key(phone)
        attempts_key = self.get_attempts_cache_key(phone)
        stored_code = cache.get(otp_key)

        # ۱. کد منقضی یا وجود ندارد
        if stored_code is None:
            messages.error(request, 'کد تایید منقضی شده است. لطفاً دوباره درخواست کد دهید.')
            request.session.pop(self.phone_session_key, None)
            return redirect(self.redirect_on_missing)

        # ۲. محدودیت تلاش
        attempts = cache.get(attempts_key, 0)
        if attempts >= self.max_attempts:
            cache.delete(otp_key)
            cache.delete(attempts_key)
            request.session.pop(self.phone_session_key, None)
            messages.error(
                request,
                f'تعداد تلاش‌ها ({self.max_attempts}) تمام شد. لطفاً کد جدید درخواست دهید.'
            )
            return redirect(self.redirect_on_missing)

        # ۳. کد صحیح
        if code == stored_code:
            cache.delete(otp_key)
            cache.delete(attempts_key)
            request.session.pop(self.phone_session_key, None)
            return self.on_success(request, phone)

        # ۴. کد اشتباه
        attempts += 1
        cache.set(attempts_key, attempts, self.attempts_ttl)
        messages.error(
            request,
            f'کد تایید صحیح نیست. (تلاش {attempts} از {self.max_attempts})'
        )
        return render(request, self.template_name, self.get_context_data())


class VerifyOtpView(BaseVerifyOtpView):
    """تایید OTP برای ورود یا ثبت‌نام"""
    template_name = 'accounts/verify_otp.html'
    phone_session_key = 'otp_phone'
    attempts_cache_prefix = 'otp_attempts'
    redirect_on_missing = 'accounts:send_otp'


    def on_success(self, request, phone):
        user = get_user_by_phone(phone)

        if user is None:
            # ✅ چک کردن نقش قبل از هدایت به ثبت‌نام
            role = request.session.get(SIGNUP_ROLE_SESSION_KEY)
            if role not in VALID_SIGNUP_ROLES:
                messages.error(request, "لطفاً نوع فعالیت خود را انتخاب کنید.")
                return redirect("accounts:select_role")

            request.session['verified_phone'] = phone
            messages.info(request, 'شماره موبایل تایید شد؛ لطفاً ثبت‌نام را کامل کنید.')
            return redirect('accounts:signup')

        # ✅ کاربر قدیمی: نقش موقت را پاک کن تا روی اکانتش اثر نگذارد
        request.session.pop(SIGNUP_ROLE_SESSION_KEY, None)

        if not user.is_active:
            messages.error(request, 'حساب کاربری شما غیرفعال است.')
            return redirect('accounts:send_otp')

        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, 'ورود با موفقیت انجام شد.')
        return redirect('website:index')

class VerifyResetOtpView(BaseVerifyOtpView):
    """تایید OTP برای بازیابی رمز عبور"""
    template_name = 'accounts/verify_reset_otp.html'
    phone_session_key = 'reset_phone'
    attempts_cache_prefix = 'otp_attempts_reset'
    redirect_on_missing = 'accounts:password_reset'

    def on_success(self, request, phone):
        request.session['reset_phone_verified'] = phone
        messages.success(request, 'شماره موبایل شما تایید شد. لطفاً رمز عبور جدید را وارد کنید.')
        return redirect('accounts:password_reset_set')


# ============================================================
# تنظیم رمز عبور جدید (مرحله سوم بازیابی رمز)
# ============================================================
class PasswordResetSetView(generic.FormView):
    """مرحله نهایی بازیابی رمز: تنظیم رمز جدید و لاگین خودکار"""
    template_name = 'accounts/password_reset_set.html'
    form_class = ResetPasswordForm

    def dispatch(self, request, *args, **kwargs):
        phone = request.session.get('reset_phone_verified')

        if not phone:
            messages.error(request, 'ابتدا شماره موبایل خود را تایید کنید.')
            return redirect('accounts:password_reset')

        self.user = get_user_by_phone(phone)

        if not self.user:
            messages.error(request, 'کاربر یافت نشد.')
            request.session.pop('reset_phone_verified', None)
            return redirect('accounts:password_reset')

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def form_valid(self, form):
        form.save()

        auth_login(
            self.request,
            self.user,
            backend="django.contrib.auth.backends.ModelBackend",
        )

        self.request.session.pop('reset_phone_verified', None)

        messages.success(
            self.request,
            'رمز عبور شما با موفقیت تغییر یافت. خوش آمدید.'
        )

        return redirect('website:index')