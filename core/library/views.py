from django.shortcuts import render

# Create your views here.
from typing import Any, Optional
from django.db import models
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views.generic.base import TemplateView, RedirectView
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import (
    ListView,
    DetailView,
    FormView,
    CreateView,
    UpdateView,
    DeleteView,
)
from meta.views import MetadataMixin
from django.db.models import F,Q
from .models import *
from django.shortcuts import get_object_or_404
from dateutil.parser import parse
from django.utils import timezone
from django.utils.decorators import method_decorator
from utils.view_counter import count_views
from django.core.exceptions import FieldError
from utils.meta_headers import GeneralMeta





class BookListView(GeneralMeta, ListView):
    """
    a class based view to show list view of books in library app
    including the meta tags
    """
    title="کتابخانه"
    description='کتاب هایی در زمینه برنامه نویسی برای توسعه دهنده گان مختلف در زیمنه پایتون و هوش مصنوعی و اینترنت اشیا'
    slug_field = 'slug'
    queryset = Book.objects.filter(status=Status.publish.value)
    template_name = "library/book-list.html"
    paginate_by = 12
    
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(title__icontains=search_q)
        if cat_slug := self.request.GET.get("category"):
            queryset = queryset.filter(category__slug__contains=cat_slug)
        if tag_slug := self.request.GET.get("tag"):
            queryset = queryset.filter(tag__slug__contains=tag_slug)
        if order_by := self.request.GET.get("order_by"):
            try:
                queryset = queryset.order_by(order_by)
            except FieldError:
                pass
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_result"] = self.get_queryset().count()
        return context


@method_decorator(count_views(session_key='visited_books'), name='dispatch')
class BookDetailView(DetailView):
    """
    a class based view to show detail page of book 
    """
    template_name = "library/book-detail.html"
    queryset = Book.objects.filter(status=Status.publish.value)
    slug_field = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meta'] = self.get_object().as_meta(self.request)
        return context
    

        