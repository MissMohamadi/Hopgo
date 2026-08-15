from django.core.exceptions import ValidationError


def validate_iranian_national_id(value):
    """
    اعتبارسنجی کد ملی ایرانی
    - تبدیل اعداد فارسی به انگلیسی
    - بررسی ۱۰ رقمی بودن
    - بررسی الگوریتم checksum کد ملی
    """
    if not value:
        raise ValidationError("کد ملی نمی‌تواند خالی باشد.")

    # تبدیل اعداد فارسی به انگلیسی
    value = value.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))
    
    # حذف فاصله و خط فاصله
    value = value.replace(" ", "").replace("-", "")
    
    # بررسی اینکه فقط عدد باشد و ۱۰ رقم باشد
    if not value.isdigit() or len(value) != 10:
        raise ValidationError("کد ملی باید دقیقاً ۱۰ رقم باشد.")
        
    # جلوگیری از اعداد تکراری مثل 1111111111
    if len(set(value)) == 1:
        raise ValidationError("کد ملی معتبر نیست.")

    # الگوریتم checksum کد ملی
    check = int(value[9])
    s = sum(int(value[i]) * (10 - i) for i in range(9))
    remainder = s % 11

    if (remainder < 2 and check == remainder) or (remainder >= 2 and check == 11 - remainder):
        return value
    else:
        raise ValidationError("کد ملی وارد شده معتبر نیست.")


def normalize_national_id(value):
    """
    نرمال‌سازی کد ملی: تبدیل اعداد فارسی به انگلیسی و حذف کاراکترهای اضافی
    """
    if not value:
        return ""
    
    value = value.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))
    value = value.replace(" ", "").replace("-", "")
    
    return value