import logging
from rest_framework.serializers import ValidationError
from aio_offline_captcha.utils import verify_offline_captcha_token

logger = logging.getLogger(__name__)

class OfflineCaptchaValidator:
    requires_context = True
    messages = {
        "captcha_invalid": "Invalid offline captcha token.",
        "captcha_error": "Error verifying captcha, please try again.",
    }

    def __init__(self, action):
        self.action = action
        self.payload = None

    def __call__(self, value, serializer_field=None):
        try:
            payload = verify_offline_captcha_token(value)
        except Exception as e:
            logger.exception("Offline captcha verification error: %s", e)
            raise ValidationError(self.messages["captcha_error"], code="captcha_error")

        if not payload:
            raise ValidationError(self.messages["captcha_invalid"], code="captcha_invalid")

        # check that action matches
        if payload.get("action") != self.action:
            logger.error("Offline captcha action mismatch: %s != %s", payload.get("action"), self.action)
            raise ValidationError(self.messages["captcha_invalid"], code="captcha_invalid")

        self.payload = payload
