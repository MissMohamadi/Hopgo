from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView, RedirectView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import (
    ListView,
    DetailView,
    FormView,
    CreateView,
    UpdateView,
    DeleteView,
)
from meta.views import MetadataMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import *
from utils.meta_headers import GeneralMeta
# Create your views here.




class DashboardHomeView(GeneralMeta, LoginRequiredMixin,HasCustomerAccess, TemplateView):
    """
    a class based view to show index page
    """
    title = "داشبورد"
    description = 'مدیریت پروفایل و سرویس ها به همراه دوره های شما'

    template_name = "dashboard/customer/home.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    


