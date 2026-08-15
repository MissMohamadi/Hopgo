
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

from website.models import NewsLetter
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import *
from dashboard.admin.forms import *
from django.db.models import F,Q
from django.core import exceptions
from utils.meta_headers import GeneralMeta


class NewsletterListView(GeneralMeta,LoginRequiredMixin,HasAdminAccess, ListView):
    title = "لیست کاربران خبرنامه"
    template_name = "dashboard/admin/newsletter/newsletter-list.html"
    paginate_by = 10
    ordering = "-created_date"


    def get_queryset(self):
        queryset = NewsLetter.objects.all().order_by("-created_date")
        search_query = self.request.GET.get('q', None)
        ordering_query = self.request.GET.get('ordering', None)

        if search_query:
            queryset = queryset.filter(
                Q(subject__icontains=search_query) | Q(content__icontains=search_query)| Q(email__icontains=search_query)
            )
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



class NewsletterDeleteView(GeneralMeta,LoginRequiredMixin,HasAdminAccess, DeleteView):
    title = "حذف کاربر از خبرنامه"
    template_name = "dashboard/admin/newsletter/newsletter-delete.html"
    success_url = reverse_lazy("dashboard:admin:newsletter-list")

    def get_queryset(self):
        return NewsLetter.objects.all()
