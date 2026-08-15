import logging
from django import forms
from django.core.exceptions import ValidationError
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.utils.translation import gettext_lazy as _
from aio_offline_captcha.form.widgets import OfflineCaptchaWidget
from django.core.signing import TimestampSigner,BadSignature, SignatureExpired

signer = TimestampSigner()


class OfflineCaptchaField(forms.CharField):
    widget = OfflineCaptchaWidget
    default_error_messages = {
        "captcha_missing": "CAPTCHA is required but was not provided.",
        "captcha_invalid": "Invalid CAPTCHA answer, please try again.",
        "captcha_expired": "CAPTCHA expired, please refresh and try again.",
    }
    
    def to_python(self, value):
        """
        value comes from widget.value_from_datadict: (user_input, token)
        """
        if value is None or not isinstance(value, (tuple, list)) or len(value) != 2:
            return None, None
        return value

    def validate(self, value):                
        user_input, token = value
        if not user_input or not token:
            raise ValidationError(self.error_messages["captcha_missing"])

        if not self.validate_captcha_token(token=token, user_input=user_input):
            raise ValidationError(self.error_messages["captcha_invalid"])
        
        
    def validate_captcha_token(self,token: str, user_input: str, max_age: int = 300) -> bool:
        try:
            original_text = signer.unsign(token, max_age=max_age)
            
        except SignatureExpired:
            raise ValidationError(self.error_messages["captcha_invalid"])
        except BadSignature:
            raise ValidationError(self.error_messages["captcha_invalid"])        
        return original_text == user_input.lower()

