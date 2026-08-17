# accounts/validators.py
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


# ============================================================
# ابزار مشترک: تبدیل اعداد فارسی/عربی به انگلیسی
# ============================================================
def _to_english_digits(value: str) -> str:
    value = value.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))
    value = value.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
    return value


# ============================================================
# نرمال‌سازی کد ملی (صفرهای ابتدایی حفظ می‌شوند!)
# ============================================================
def normalize_national_id(value) -> str:
    if value is None:
        return ""
    value = _to_english_digits(str(value).strip())
    value = value.replace(" ", "").replace("-", "")
    return value


# ============================================================
# نرمال‌سازی شماره موبایل به فرمت 09xxxxxxxxx
# ============================================================
def normalize_phone(value) -> str:
    if value is None:
        return ""
    value = _to_english_digits(str(value).strip())
    value = re.sub(r"[\s\-\(\)]", "", value)

    if value.startswith("+"):
        value = value[1:]
    if value.startswith("0098"):
        value = "0" + value[4:]
    elif value.startswith("98") and len(value) == 12:
        value = "0" + value[2:]
    if value.startswith("9") and len(value) == 10:
        value = "0" + value

    return value


# ============================================================
# اعتبارسنجی کد ملی با الگوریتم checksum
# ============================================================
def validate_iranian_national_id(value):
    value = normalize_national_id(value)

    if not value.isdigit() or len(value) != 10:
        raise ValidationError(_("کد ملی باید دقیقاً ۱۰ رقم باشد."))

    if len(set(value)) == 1:
        raise ValidationError(_("کد ملی وارد شده معتبر نیست."))

    # الگوریتم checksum کد ملی ایرانی
    total = sum(int(value[i]) * (10 - i) for i in range(9))
    remainder = total % 11
    expected = remainder if remainder < 2 else 11 - remainder

    if expected != int(value[9]):
        raise ValidationError(_("کد ملی وارد شده معتبر نیست."))


# ============================================================
# اعتبارسنجی شماره موبایل ایرانی
# ============================================================
def validate_phone_number(value):
    normalized = normalize_phone(value)
    if not re.match(r"^09\d{9}$", normalized):
        raise ValidationError(
            _('شماره درج شده فرمت درستی ندارد'),
            params={'value': value},
        )