
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
from dashboard.admin.forms import *
from django.db.models import F,Q
from django.core import exceptions
from django.core.exceptions import FieldError
from utils.meta_headers import GeneralMeta

