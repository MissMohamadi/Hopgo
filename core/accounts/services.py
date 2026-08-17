import logging
import random
import requests
from decouple import config

from django.conf import settings

logger = logging.getLogger(__name__)

def generate_otp_code(length: int = 5) -> str:
    """تولید کد تایید ۵ رقمی رندوم"""
    return str(random.randint(10000, 99999))


class SmsIrService:
    """
    send sms services by sms.ir
    """    
    BASE_URL = "https://api.sms.ir/v1/send/verify"

    @classmethod
    def send_otp(cls, phone: str, code: str) -> tuple[bool, str]:
        """
        send verification code
        
        Args:
            phone: شماره موبایل کاربر
            code: کد تایید
            
        Returns:
            tuple[bool, str]: (موفقیت, پیام)
        """
        api_key = config("SMS_IR_API_KEY", default="")
        template_id = config("SMS_IR_TEMPLATE_ID", cast=int, default=0)
        code_param = config("SMS_IR_TEMPLATE_CODE_PARAM", default="Code")

        if not api_key or not template_id:
            logger.error("SMS_IR_API_KEY یا SMS_IR_TEMPLATE_ID تنظیم نشده است.")
            return False, "تنظیمات سرویس پیامک کامل نیست."

        headers = {
            "Content-Type": "application/json",
            "Accept": "text/plain",
            "x-api-key": api_key,
        }

        payload = {
            "mobile": phone,
            "templateId": template_id,
            "parameters": [
                {
                    "name": code_param,
                    "value": code,
                }
            ],
        }

        masked_phone = f"{phone[:4]}****{phone[-4:]}" if len(phone) >= 8 else "***"

        try:
            response = requests.post(cls.BASE_URL, json=payload, headers=headers, timeout=10)
            result = response.json()

            if response.status_code == 200 and result.get("status") == 1:
                return True, result.get("message", "موفق")

            logger.error(
                "SMS.ir error for %s: status_code=%s result=%s",
                masked_phone,  
                response.status_code,
                result,
            )

            return False, result.get("message", "خطا در ارسال پیامک")

        except requests.exceptions.RequestException as e:
            logger.exception(
                "Request exception while sending SMS to %s: %s", 
                masked_phone, 
                str(e)
            )
            return False, "خطا در ارتباط با سرویس پیامک"


def send_otp_code(mobile: str, code: str) -> tuple[bool, str]:
    """
    ارسال کد تایید بر اساس settings.OTP_SEND_MODE
    - smsir: ارسال پیامک واقعی
    - console: چاپ در ترمینال (توسعه/تست)
    """
    if settings.OTP_SEND_MODE == "smsir":
        return SmsIrService.send_otp(mobile, code)

    # حالت کنسول (توسعه)
    print("\n" + "=" * 45)
    print(f"🔑 کد تایید برای {mobile}  =>  {code}")
    print("=" * 45 + "\n")
    return True, "کد تایید در کنسول چاپ شد (حالت تست)"