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
from django.conf import settings
from .models import *
from .forms import ContactForm, NewsLetterForm
from utils.meta_headers import GeneralMeta
# Create your views here.
from django.utils.decorators import method_decorator


class IndexView(GeneralMeta, TemplateView):
    """
    a class based view to show index page
    """
    title = "پلتفرم hopgo"
    description = 'ارائه دهنده سرویس های مختلف پت'
    template_name = "website/index.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


class AboutView(GeneralMeta, TemplateView):
    """
    a class based view to show About page
    """
    title = "درباره من"
    description = 'من علی بیگدلی توسعه دهنده بک اند پایتون و جنگو هستم و به مدت بیش از 8 سال در زمینه توسعه اینترنت اشیا و هوش مصنوعی فعالیت داشتم و در پروژه های بین امللی تاثیر گذار بودم'

    template_name = "website/about-me.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


class ContactView(GeneralMeta, TemplateView):
    """
    a class based view to show Contact page
    """
    title = "تماس با من"
    description = 'ارتباط  با من و مشاوره در حوزه های مختلف فناوری'
    template_name = "website/contact-me.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContactForm()
        return context


class TicketView(CreateView):
    """
    a class based view to show index page
    """
    http_method_names = ['post']
    form_class = ContactForm

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request, 'تیکت شما با موفقیت ثبت شد و در اسرع وقت با شما تماس حاصل خواهد شد')
        return super().form_valid(form)

    def form_invalid(self, form):
        # handle unsuccessful form submission
        messages.error(
            self.request, 'مشکلی در ارسال فرم شما پیش آمد لطفا ورودی ها رو بررسی کنین و مجدد ارسال نمایید')
        return redirect(self.request.META.get('HTTP_REFERER'))

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')


class CounselingOrMentorRequestView(GeneralMeta, TemplateView):
    """
    a class based view to show Contact page
    """
    title = "درخواست مشاوره یا منتور"
    description = 'درخواست مشاوره آموزشی برای اینکه چطور به یک توسعه دهنده پایتون تبدیل بشیم'

    template_name = "website/counseling-or-mentor-request.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContactForm()
        return context


class ProjectRequestView(GeneralMeta, TemplateView):
    """
    a class based view to show Contact page
    """
    title = "سفارش پروژه"
    description = 'سفارش پروژه های مبتنی بر توسعه بک اند پایتون'
    template_name = "website/project-request.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContactForm()
        return context


class SecurityRoadMapView(GeneralMeta, TemplateView):
    """
    a class based view to show index page
    """
    title = "نقشه راه امینت وب "
    description = 'چطور باید به توسعه دهنده backend پایتون تبدیل بشید و چه چیز هایی رو لازم هستش که یاد بگیرید. '

    template_name = "website/security-road-map.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


class PolicyAndPrivacyView(GeneralMeta, TemplateView):
    """
    a class based view to show index page
    """
    title = "شرایط و قوانین استفاده از سایت"
    description = 'قوانینی که می بایست در استفاده از سایت از آن ها آگاه باشید'

    template_name = "website/policy-and-privacy.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)




class NewsletterView(CreateView):
    http_method_names = ['post']
    form_class = NewsLetterForm
    success_url = '/'

    def form_valid(self, form):
        # handle successful form submission
        messages.success(
            self.request, 'از ثبت نام شما ممنونم، اخبار جدید رو براتون ارسال می کنم 😊👍')
        return super().form_valid(form)

    def form_invalid(self, form):
        # handle unsuccessful form submission
        messages.error(
            self.request, 'مشکلی در ارسال فرم شما وجود داشت که می دونم برا چی بود!! چون ربات هستید!')
        return redirect('website:index')



class ConnectView(GeneralMeta, TemplateView):
    title = "ارتباط با علی بیگدلی | توسعه‌دهنده بک‌اند پایتون و Django"
    description = "علی بیگدلی، توسعه‌دهنده بک‌اند پایتون با تخصص Django. برای همکاری، شبکه‌سازی، پروژه‌های فریلنسری و ارتباط حرفه‌ای از این صفحه با من در تماس باشید."

    template_name = "website/connect.html"
