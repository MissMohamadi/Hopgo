from meta.views import MetadataMixin
from django.conf import settings
# Create your views here.


class GeneralMeta(MetadataMixin):
    locale = 'fa_IR'

    def get_meta_url(self, context=None):
        return self.request.build_absolute_uri()

    def get_meta_og_title(self, context=None):
        return self.title


    def get_meta_schemaorg_title(self, context=None):
        return self.title
    