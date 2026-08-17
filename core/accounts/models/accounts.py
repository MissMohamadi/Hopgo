from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from ..validators import (
    validate_iranian_national_id, 
    normalize_national_id, 
    normalize_phone, 
)


class UserType(models.IntegerChoices):
    customer = 1 , _('owner')
    supervisor = 2, _('walker')
    admin = 10, _('admin')
    


class UserManager(BaseUserManager):
    """
    Custom user model manager where national_id is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError(_("نام کاربری الزامی است"))
        if not email:
            raise ValueError(_("ایمیل الزامی است"))
            
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, username,email, password, **extra_fields):
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
        return self.create_user(username, email, password, **extra_fields)


AUTH_PROVIDERS = {'facebook': 'facebook', 'google': 'google',
                  'twitter': 'twitter', 'email': 'email'}


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(_("username"), unique=True,max_length=255)
    first_name = models.CharField(max_length=255,blank=True,null=True)
    last_name = models.CharField(max_length=255,blank=True,null=True)
    phone_number = models.CharField(
        max_length=11, 
        unique=True, 
        blank=True, 
        null=True, 
        verbose_name="شماره موبایل"
    )
    national_id = models.CharField(max_length=10,validators=[validate_iranian_national_id],
                                   verbose_name="کد ملی",null=True,blank=True,unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    type = models.IntegerField(choices=UserType.choices,default=UserType.customer.value)
    auth_provider = models.CharField(
        max_length=255, blank=False,
        null=False, default=AUTH_PROVIDERS.get('email'))
    

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = UserManager()

    def __str__(self):
        return self.masked_national_id or self.email or f"User {self.pk}"

    def clean(self):
        super().clean()
        if self.national_id:
            self.national_id = normalize_national_id(self.national_id)
        if self.phone_number:
            self.phone_number = normalize_phone(self.phone_number)

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)

    @property
    def masked_national_id(self):
        national_id = self.national_id or ""

        if len(national_id) < 5:
            return "***"

        return f"{national_id[:3]}*****{national_id[-2:]}"

    @property
    def masked_phone(self):
        phone = self.phone_number or ""
        if len(phone) < 8:
            return "***"
        return f"{phone[:4]}****{phone[-4:]}"

    def __str__(self):
        return self.username or self.email or f"User {self.pk}"



