from typing import Iterable, Optional
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from accounts.validators import validate_iranian_national_id, normalize_national_id

from django.db import models
import random 
import string

from ..utils import normalize_phone_number

class UserType(models.IntegerChoices):
    customer = 1 , _('dog owner')
    supervisor = 2, _('dog walker')
    admin = 10, _('admin')
    




class UserManager(BaseUserManager):
    """
    Custom user model manager where national_id is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, national_id, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not national_id:
            raise ValueError(_("The national_id must be set"))
        user = self.model(national_id=national_id, **extra_fields)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("is_active", True)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, national_id, password, **extra_fields):
        """
        Create and save a SuperUser with the given national_id and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("type", UserType.admin.value)
        

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(national_id, password, **extra_fields)


AUTH_PROVIDERS = {'facebook': 'facebook', 'google': 'google',
                  'twitter': 'twitter', 'email': 'email'}


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(_("email address"))
    username = models.CharField(_("username"), unique=True,blank=True,null=True,max_length=255)
    first_name = models.CharField(max_length=255,blank=True,null=True)
    last_name = models.CharField(max_length=255,blank=True,null=True)
    phone_number = models.CharField(max_length=25)
    national_id = models.CharField(max_length=20,validators=[validate_iranian_national_id],
                                   verbose_name="کد ملی",null=False,blank=False,unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    type = models.IntegerField(choices=UserType.choices,default=UserType.customer.value)
    auth_provider = models.CharField(
        max_length=255, blank=False,
        null=False, default=AUTH_PROVIDERS.get('email'))
    

    USERNAME_FIELD = "national_id"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def clean(self):
        super().clean()
        if self.national_id:
            self.national_id = normalize_national_id(self.national_id)
        if self.national_id:
                self.national_id = normalize_national_id(self.national_id)
        if self.phone_number:
                self.phone_number = normalize_phone_number(self.phone_number)
        

    def save(self, *args, **kwargs):
        if not self.pk:
            self.username = str(self.email).split('@')[0]
            suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
            if User.objects.filter(username=self.username).exists():
                self.username += suffix
        super(User, self).save(*args, **kwargs)

    @property
    def masked_national_id(self):
        national_id = self.national_id or ""

        if len(national_id) < 5:
            return "***"

        return f"{national_id[:3]}*****{national_id[-2:]}"




