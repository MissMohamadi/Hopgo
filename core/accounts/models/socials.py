from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ProviderType(models.IntegerChoices):
    google = 1 , "google"
    github = 2 , "github"

class SocialProfileModel(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="social_profile")
    provider = models.IntegerField(choices=ProviderType.choices,default=ProviderType.google.value)
    unique_id = models.CharField(max_length=255)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        
        return f"{self.user} - {ProviderType(self.provider).name}"