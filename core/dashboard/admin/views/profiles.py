from typing import Any
from django.db import models
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
from accounts.models import ProfileModel,SocialProfileModel,ProviderType
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from django.contrib.auth import views, get_user_model, forms
from django.contrib.auth import logout
from utils.meta_headers import GeneralMeta
from dashboard.admin.forms import AdminPasswordChangeForm,AdminProfileForm
from dashboard.permissions import *
User = get_user_model()


class ProfileEditView(GeneralMeta, LoginRequiredMixin,HasAdminAccess, UpdateView):
    """
    a class based view to show profile edit page
    """
    title = "ویرایش اطلاعات کاربری"
    description = 'مدیریت پروفایل و سرویس ها به همراه دوره های شما'

    template_name = "dashboard/admin/profiles/profile-edit.html"
    form_class = AdminProfileForm    
    success_url = reverse_lazy('dashboard:admin:profile-edit')

    def get_object(self, queryset=None):
        # Return the Profile object associated with the current user.
        return ProfileModel.objects.get(user=self.request.user)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(
            self.request, 'اطلاعات کاربری شما با موفقیت تغییر کرد')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{error}")
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context  = super().get_context_data(**kwargs)
        context["social_google"] = SocialProfileModel.objects.filter(user=self.request.user,provider=ProviderType.google.value).exists()
        context["social_github"] = SocialProfileModel.objects.filter(user=self.request.user,provider=ProviderType.github.value).exists()
        context["form_password"] = AdminPasswordChangeForm(self.request.user)        
        return context


class ProfileAvatarEditView(GeneralMeta, LoginRequiredMixin,HasAdminAccess, UpdateView):
    """
    a class based view to show profile edit page
    """
    http_method_names = ['post']
    model = ProfileModel
    fields = ['image']
    success_url = reverse_lazy('dashboard:admin:profile-edit')

    def get_object(self, queryset=None):
        # Return the Profile object associated with the current user.
        return ProfileModel.objects.get(user=self.request.user)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(self.request, 'تصویر کاربری شما با موفقیت تغییر کرد')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{error}")
        return redirect(reverse_lazy('dashboard:admin:profile-edit'))
    


class ProfilePasswordEditView(GeneralMeta, LoginRequiredMixin,HasAdminAccess, FormView):
    """
    a class based view to show profile edit page
    """
    http_method_names = ['post']
    success_url = reverse_lazy('accounts:login')
    form_class = AdminPasswordChangeForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request, 'گذرواژه شما با موفقیت تغییر کرد، لطفا مجدد وارد بشید.')

        logout(self.request)
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{error}")
        return redirect(reverse_lazy('dashboard:admin:profile-edit'))
