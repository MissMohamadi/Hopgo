from django.contrib.auth import get_user_model
from .validators import normalize_phone

User = get_user_model()

def get_user_by_phone(phone: str):
    """
    پیدا کردن کاربر بر اساس شماره موبایل از مدل User
    """
    if not phone:
        return None
    
    # نرمال‌سازی شماره برای اطمینان از تطابق با دیتابیس
    normalized_phone = normalize_phone(phone)
    
    try:
        return User.objects.get(phone_number=normalized_phone)
    except User.DoesNotExist:
        return None
    except User.MultipleObjectsReturned:
        # اگر به هر دلیلی داده تکراری قدیمی وجود داشت
        return User.objects.filter(phone_number=normalized_phone).first()
def normalize_phone_number(phone: str) -> str:
    if not phone:
        return ""

    phone = phone.strip()

    # تبدیل اعداد فارسی به انگلیسی
    fa_digits = "۰۱۲۳۴۵۶۷۸۹"
    en_digits = "0123456789"

    translation_table = str.maketrans(fa_digits, en_digits)
    phone = phone.translate(translation_table)

    # حذف کاراکترهای اضافی
    phone = phone.replace(" ", "")
    phone = phone.replace("-", "")
    phone = phone.replace("_", "")

    # تبدیل +98 به 0
    if phone.startswith("+98"):
        phone = "0" + phone[3:]

    # تبدیل 98 به 0
    if phone.startswith("98") and len(phone) == 12:
        phone = "0" + phone[2:]

    # اگر کاربر فقط با 9 شروع کرده باشد
    if phone.startswith("9") and len(phone) == 10:
        phone = "0" + phone

    return phone        