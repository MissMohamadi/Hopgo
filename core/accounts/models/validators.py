import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_minimum_size(width=None, height=None):
    def validator(image):
        error = False
        if width is not None and image.width < width:
            error = True
        if height is not None and image.height < height:
            error = True
        if error:
            raise ValidationError(
                [f'Size should be at least {width} x {height} pixels.']
            )

    return validator




def validate_phone_number(value):
    pattern = r'^\+?\d{1,3}[-\.\s]?\(?\d{3}\)?[-\.\s]?\d{3}[-\.\s]?\d{4}$'
    if not re.match(pattern, value):
        raise ValidationError(
            _('شماره درج شده فرمت درستی ندارد'),
            params={'value': value},
        )