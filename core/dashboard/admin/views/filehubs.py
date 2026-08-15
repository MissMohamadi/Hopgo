
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

from filehub.models import UploadedFile
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import *
from dashboard.admin.forms import *
from django.db.models import F,Q
from django.core import exceptions
from utils.meta_headers import GeneralMeta



class FileHubListView(GeneralMeta,LoginRequiredMixin,HasAdminAccess, ListView):
    title = "لیست فایل ها"
    template_name = "dashboard/admin/filehub/filehub-list.html"
    paginate_by = 10
    ordering = "-created_date"

       
    def get_queryset(self):
        queryset = UploadedFile.objects.all().order_by("-created_date")
        search_query = self.request.GET.get('q', None)
        ordering_query = self.request.GET.get('ordering', None)

        if search_query:
            queryset = queryset.filter(
                file__name__icontains=search_query)
            
        if ordering_query:
            try:
                queryset = queryset.order_by(ordering_query)
            except exceptions.FieldError:
                pass
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_result"] = self.get_queryset().count()
        return context



class FileHubCreateView(GeneralMeta,LoginRequiredMixin,HasAdminAccess, CreateView):
    title = "ایجاد یک فایل"
    template_name = "dashboard/admin/filehub/filehub-create.html"
    model = UploadedFile
    fields = ['file']
    success_url = reverse_lazy("dashboard:admin:filehub-list")

    def form_valid(self, form):
        messages.success(self.request,"فایل با موفقیت ایجاد شد")
        return super().form_valid(form)
    



class FileHubDeleteView(GeneralMeta,LoginRequiredMixin,HasAdminAccess, DeleteView):
    title = "حذف یک فایل"
    template_name = "dashboard/admin/filehub/filehub-delete.html"
    success_url = reverse_lazy("dashboard:admin:filehub-list")

    def get_queryset(self):
        return UploadedFile.objects.all()
