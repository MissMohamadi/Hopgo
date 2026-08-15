import uuid
from django.forms import widgets
# returns {image_base64, token}
from aio_offline_captcha.utils import generate_captcha


class OfflineCaptchaBase(widgets.Widget):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uuid = uuid.uuid4().hex

    def get_context(self, name, value, attrs):
        captcha_data = generate_captcha()
        context = super().get_context(name, value, attrs)
        context.update({
            "widget_uuid": self.uuid,
            "captcha_image": captcha_data["image_base64"],
            "captcha_token": captcha_data["token"],            
        })
        return context

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs["data-widget-uuid"] = self.uuid
        return attrs
    


class OfflineCaptchaWidget(OfflineCaptchaBase):
    template_name = "aio_offline_captcha/offline_captcha_widget.html"
    
    def value_from_datadict(self, data, files, name):
        """
        Collect both the user input and the token from POST.
        Returns a tuple (user_input, token)
        """
        user_input = data.get(name)
        token = data.get("captcha_token")
        return user_input, token
