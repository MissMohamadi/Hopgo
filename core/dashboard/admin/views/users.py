
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView, RedirectView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    ListView,
    DetailView,
    FormView,
    CreateView,
    UpdateView,
    DeleteView,
    View
)
from meta.views import MetadataMixin

from accounts.models import UserType
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import *
from dashboard.admin.forms import *
from django.contrib.auth import get_user_model
from django.db.models import F,Q
from django.core import exceptions
from utils.meta_headers import GeneralMeta
from django.http.response import JsonResponse

User = get_user_model()



class UserListView(GeneralMeta,LoginRequiredMixin,HasAdminAccess, ListView):
    title = "لیست کاربران"
    template_name = "dashboard/admin/users/user-list.html"
    paginate_by = 10
    ordering = "-created_date"
    
    def get_queryset(self):
        queryset = User.objects.filter(Q(is_superuser=False), ~Q(type=UserType.admin.value)).order_by("-created_date")
        search_query = self.request.GET.get('q', None)
        ordering_query = self.request.GET.get('ordering', None)

        if search_query:
            queryset = queryset.filter(
                email__icontains=search_query
            )
        if ordering_query:
            try:
                queryset = queryset.order_by(ordering_query)
            except exceptions.FieldError:
                pass

            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_types"] = UserType.choices
        
        return context




class UserEditView(GeneralMeta,LoginRequiredMixin,HasAdminAccess, UpdateView):
    title = "ویرایش کاربر"
    template_name = "dashboard/admin/users/user-edit.html"
    form_class = UserForm
    
    def get_queryset(self):
        return User.objects.filter(Q(is_superuser=False), ~Q(type=UserType.admin.value))
  

    def form_valid(self, form):
        super().form_valid(form)
        messages.success(self.request,"اطلاعات کاربر با موفقیت تغییر کرد")
        return redirect(reverse_lazy("dashboard:admin:user-edit", kwargs={"pk": form.instance.pk}))
    
    def form_invalid(self, form):
        super().form_invalid(form)
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return redirect(reverse_lazy("dashboard:admin:user-edit", kwargs={"pk": form.instance.pk}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_types"] = UserType.choices
        return context
    
    def get_success_url(self):
        user_object = self.get_object()
        return reverse_lazy("dashboard:admin:user-edit", kwargs={"pk": user_object.pk})



class UserDeleteView(GeneralMeta,LoginRequiredMixin,HasAdminAccess, DeleteView):
    title = "حذف کاربر"
    template_name = "dashboard/admin/users/user-delete.html"
    success_url = reverse_lazy("dashboard:admin:user-list")

    def get_queryset(self):
        return User.objects.filter(Q(is_superuser=False), ~Q(type=UserType.admin.value))



class UserBriefListView(GeneralMeta,LoginRequiredMixin,HasAdminAccess, View):

    def get_queryset(self):
        queryset = User.objects.filter(Q(is_superuser=False)| ~Q(type=UserType.admin.value)).prefetch_related("user_profile").order_by("-created_date")
        search_query = self.request.GET.get('q', None)
   

        if search_query:
            queryset = queryset.filter(
                Q(email__icontains=search_query)|
                Q(user_profile__first_name__icontains=search_query)|
                Q(user_profile__last_name__icontains=search_query),
            )
        return queryset

    def get(self,request,*args, **kwargs):
        users = list(self.get_queryset().values(
        "id",
        "email",
        "user_profile__first_name",
        "user_profile__last_name"
        ))
        return JsonResponse({'users': users})
    
    

class UserResetPasswordView(LoginRequiredMixin,HasAdminAccess, FormView):
    template_name = "dashboard/admin/users/user-password-reset.html"
    form_class = UserResetPasswordForm
    
    def get_object(self):
        return get_object_or_404(User, pk=self.kwargs["pk"])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object"] = self.get_object()
        return context

    def form_valid(self, form):
        user = self.get_object()
        user.set_password(form.cleaned_data["new_password"])
        user.save()

        messages.success(
            self.request,
            f"پسورد کاربر  {user.get_username()} تغییر یافت"
        )
        return super().form_valid(form)

    def get_success_url(self):
        user_object = self.get_object()
        return reverse_lazy("dashboard:admin:user-edit", kwargs={"pk": user_object.pk})