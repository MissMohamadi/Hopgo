from typing import Any, Dict, Optional
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

from website.models import Ticket,TicketType
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import *
from dashboard.admin.forms import *
from django.db.models import F,Q
from django.core import exceptions
from utils.meta_headers import GeneralMeta



class TicketListView(GeneralMeta,LoginRequiredMixin,HasAdminAccess, ListView):
    template_name = "dashboard/admin/support/ticket-list.html"
    paginate_by = 10
    ordering = "-created_date"
    title = "لیست تیکت ها"

    def get_queryset(self):
        queryset = Ticket.objects.all().order_by("-created_date")
        search_query = self.request.GET.get('q', None)
        ordering_query = self.request.GET.get('ordering', None)
        ticket_type_query = self.request.GET.get('ticket_type', None)

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(content__icontains=search_query)
            )
        if ordering_query:
            try:
                queryset = queryset.order_by(ordering_query)
            except exceptions.FieldError:
                pass
        if ticket_type_query:
            try:
                queryset = queryset.filter(Q(type=ticket_type_query))
            except exceptions.FieldError:
                pass

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_result"] = self.get_queryset().count()
        context["ticket_types"] = TicketType.choices
        return context


class TicketDetailView(GeneralMeta,LoginRequiredMixin,HasAdminAccess, DetailView):
    template_name = "dashboard/admin/support/ticket-detail.html"
    title = "جزئیات تیکت"

    def get_queryset(self):
        return Ticket.objects.all()
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not obj.is_seen:
            obj.is_seen = True
            obj.save()
        return obj



class TicketDeleteView(GeneralMeta,LoginRequiredMixin,HasAdminAccess, DeleteView):
    template_name = "dashboard/admin/support/ticket-delete.html"
    success_url = reverse_lazy("dashboard:admin:ticket-list")
    title = "حذف تیکت"
    

    def get_queryset(self):
        return Ticket.objects.all()
