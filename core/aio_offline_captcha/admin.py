from django.contrib import admin
from django.contrib.admin.forms import AdminAuthenticationForm

from aio_offline_captcha.form.fields import OfflineCaptchaField
from aio_offline_captcha.form.widgets import OfflineCaptchaWidget
from aio_offline_captcha.app_settings import OFFLINE_CAPTCHA_ADMIN_ENABLE


# Add offline captcha to admin login form
class CustomAdminAuthenticationForm(AdminAuthenticationForm):
    captcha = OfflineCaptchaField(widget=OfflineCaptchaWidget())


if OFFLINE_CAPTCHA_ADMIN_ENABLE:
    admin.autodiscover()
    admin.site.login_form = CustomAdminAuthenticationForm
    admin.site.login_template = "aio_offline_captcha/login.html"
