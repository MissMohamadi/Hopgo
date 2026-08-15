from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.contrib.auth import get_user_model
from pilkit.processors import Thumbnail
from imagekit.models import ImageSpecField
from .validators import *
User = get_user_model()


class ProfileModel(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_profile")
    title = models.CharField(max_length=255,null=True,blank=True)
    bio = models.TextField(blank=True,null=True)
    resume_url = models.URLField(blank=True,null=True)
    image = models.ImageField(
        upload_to='images/profile', default='images/profile/default.jpg')
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True,validators=[validate_phone_number])
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    
    image_large = ImageSpecField(source='image',
                                 processors=[Thumbnail(500,500)],
                                 format='WEBP',
                                 options={'quality': 60})
    image_medium = ImageSpecField(source='image',
                                  processors=[Thumbnail(300, 300)],
                                  format='WEBP',
                                  options={'quality': 60})
    image_small = ImageSpecField(source='image',
                                 processors=[Thumbnail(150, 150)],
                                 format='WEBP',
                                 options={'quality': 60})
    
    
    def __str__(self):
        return self.user.email

    
    @property
    def get_fullname(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return f"کاربر جدید {self.id}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        ProfileModel.objects.get_or_create(user=instance)
