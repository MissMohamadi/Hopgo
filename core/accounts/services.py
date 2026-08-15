import logging

import requests
from decouple import config

logger = logging.getLogger(__name__)


def send_sms_ir_otp(phone: str, code: str) -> tuple[bool, str]:
    """
    ارسال کد تایید یک‌بارمصرف با قالب sms.ir
    خروجی:
    (True, message) در صورت موفقیت
    (False, message) در صورت خطا
    """

    api_key = config("SMS_IR_API_KEY", default="")
    template_id = config("SMS_IR_TEMPLATE_ID", cast=int, default=0)
    code_param = config("SMS_IR_TEMPLATE_CODE_PARAM", default="Code")

    if not api_key or not template_id:
        logger.error("SMS_IR_API_KEY یا SMS_IR_TEMPLATE_ID تنظیم نشده است.")
        return False, "تنظیمات سرویس پیامک کامل نیست."

    url = "https://api.sms.ir/v1/send/verify"

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

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        result = response.json()

        if response.status_code == 200 and result.get("status") == 1:
            return True, result.get("message", "موفق")

        logger.error(
            "SMS.ir error: status_code=%s result=%s",
            response.status_code,
            result,
        )

        return False, result.get("message", "خطا در ارسال پیامک")

    except requests.exceptions.RequestException as e:
        logger.exception("Request exception while sending SMS: %s", str(e))
        return False, "خطا در ارتباط با سرویس پیامک"