
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

from library.models import Book, BookCategory, BookTag, Status
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import *
from dashboard.admin.forms import *
from django.db.models import F,Q
from django.core import exceptions
from utils.meta_headers import GeneralMeta




class BookListView(GeneralMeta,LoginRequiredMixin,HasAdminAccess, ListView):
    template_name = "dashboard/admin/library/book-list.html"
    paginate_by = 10
    title = "لیست کتاب ها"
    
    def get_queryset(self):
        queryset = Book.objects.filter(user=self.request.user).order_by("-created_date")
        search_query = self.request.GET.get('q', None)
        ordering_query = self.request.GET.get('ordering', None)
        category_query = self.request.GET.get('category', None)

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(content__icontains=search_query)
            )
        if ordering_query:
            try:
                queryset = queryset.order_by(ordering_query)
            except exceptions.FieldError:
                pass
        if category_query:
            try:
                queryset = queryset.filter(Q(category__slug__icontains=category_query)|Q(category__title__icontains=category_query))
            except exceptions.FieldError:
                pass
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = BookCategory.objects.all()
        context["statuses"] = Status.choices
        context["total_result"] = self.get_queryset().count()
        return context


class BookDetailView(GeneralMeta,LoginRequiredMixin,HasAdminAccess, DetailView):
    template_name = "dashboard/admin/library/book-detail.html"
    title = "پیش نمایش کتاب"

    def get_queryset(self):
        books = Book.objects.filter(user=self.request.user)
        return books


class BookCreateView(GeneralMeta,LoginRequiredMixin,HasAdminAccess, CreateView):
    template_name = "dashboard/admin/library/book-create.html"
    form_class = BookForm
    success_url = None
    title = "ایجاد کتاب جدید"

    def form_valid(self, form):
        form.instance.user = self.request.user
        super().form_valid(form)
        messages.success(self.request,"کتاب با موفقیت ایجاد شد")
        return redirect(reverse_lazy("dashboard:admin:book-edit", kwargs={"pk": form.instance.pk}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = BookCategory.objects.all()
        context["statuses"] = Status.choices
        return context


class BookEditView(GeneralMeta,LoginRequiredMixin,HasAdminAccess, UpdateView):
    template_name = "dashboard/admin/library/book-edit.html"
    form_class = BookForm
    title = "ویرایش کتاب"

    def get_queryset(self):
        books = Book.objects.filter(user=self.request.user)
        return books

    def form_valid(self, form):
        form.instance.user = self.request.user
        super().form_valid(form)
        messages.success(self.request,"کتاب با موفقیت ویرایش شد")
        return redirect(reverse_lazy("dashboard:admin:book-edit", kwargs={"pk": form.instance.pk}))
    
    def form_invalid(self, form):
        print(form.data)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = BookCategory.objects.all()
        context["statuses"] = Status.choices
        return context


class BookDeleteView(GeneralMeta,LoginRequiredMixin,HasAdminAccess, DeleteView):
    template_name = "dashboard/admin/library/book-delete.html"
    success_url = reverse_lazy("dashboard:admin:book-list")
    title = "حذف یک کتاب"

    def get_queryset(self):
        books = Book.objects.filter(user=self.request.user)
        return books



class BookCategoryListView(GeneralMeta, LoginRequiredMixin, HasAdminAccess, ListView):
    template_name = "dashboard/admin/library/category-list.html"
    paginate_by = 10
    ordering = "-created_date"
    title = "لیست دسته بندی کتاب"


    def get_queryset(self):
        queryset = BookCategory.objects.all().order_by('-id')
        search_query = self.request.GET.get('q', None)


        if search_query:
            queryset = queryset.filter(
                title__icontains=search_query
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_result"] = self.get_queryset().count()
        return context


class BookCategoryCreateView(GeneralMeta, LoginRequiredMixin, HasAdminAccess, SuccessMessageMixin, CreateView,):
    template_name = "dashboard/admin/library/category-create.html"
    title = "ساخت دسته بندی کتاب"
    form_class = BookCategoryForm
    success_url = reverse_lazy("dashboard:admin:book-category-list")
    success_message = 'دسته بندی جدید با موفقیت ثبت شد'


class BookCategoryEditView(GeneralMeta, LoginRequiredMixin, HasAdminAccess, SuccessMessageMixin, UpdateView):
    template_name = "dashboard/admin/library/category-edit.html"
    title = "ویرایش دسته بندی کتاب"
    form_class = BookCategoryForm
    success_message = 'دسته بندی  با موفقیت ویرایش شد'

    def get_queryset(self):
        return BookCategory.objects.all()

    def get_success_url(self):
        category_object = self.get_object()
        return reverse_lazy("dashboard:admin:book-category-edit", kwargs={"pk": category_object.pk})


class BookCategoryDeleteView(GeneralMeta, LoginRequiredMixin, HasAdminAccess, SuccessMessageMixin, DeleteView):
    template_name = "dashboard/admin/library/category-delete.html"
    success_url = reverse_lazy("dashboard:admin:book-category-list")
    success_message = 'دسته بندی  با موفقیت حذف شد'
    title = "حذف دسته بندی کتاب"

    def get_queryset(self):
        return BookCategory.objects.all()
