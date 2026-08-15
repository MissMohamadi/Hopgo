from django.utils.deprecation import MiddlewareMixin
from .models import BlackList
from django.http import HttpResponseForbidden
from django.core.cache import cache

class HoneyPotMiddleware(MiddlewareMixin):
    def process_request(self, request):
        assert hasattr(request, "session"), (
            "The Django authentication middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE_CLASSES setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        )
        
        # print(request.__dict__)
        self.client_ip = self.get_client_ip(request)
        blacklist_list = cache.get('blacklist_list')
        if blacklist_list is None:
            blacklist_list = BlackList.objects.all()
            cache.set('blacklist_list', blacklist_list, 600)
        if blacklist_list.filter(ip_address=self.client_ip).exists():
            return HttpResponseForbidden("You are not allowed to call the website anymore. YOU ARE BANNED!")
            
        
        
    def get_client_ip(self,request):
        x_forwarded_for = request.META.get('HTTP_REMOTE_ADDR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

        