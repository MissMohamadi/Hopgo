from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView, RedirectView,View
from django.contrib import messages
from django.shortcuts import redirect
from django.core.cache import cache
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from dashboard.permissions import *
from utils.meta_headers import GeneralMeta


class ResetCacheView(GeneralMeta, LoginRequiredMixin,HasAdminAccess, View):
    """
    a class based view to show profile edit page
    """

    def get(self,request,*args, **kwargs):
        cache.clear()
        messages.success(request,"کش با موفقیت ریست شد")
        return redirect(reverse_lazy('dashboard:admin:home'))