# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ProfileModel, SocialProfileModel


class UserAdminConfig(UserAdmin):
    model = User
    search_fields = ("email", "username", "phone_number")  # ✅ اضافه شد
    list_filter = ("email", "username", "is_active", "is_staff", "type")
    ordering = ("-created_date",)
    list_display = ("username", "phone_number","email" ,"is_active", "is_staff", "is_verified", "type")  
    
    fieldsets = (
        ("Authentication", {"fields": ("username", "phone_number", "password", "email")}), 
        ("Permissions", {"fields": ("is_staff", "is_active", "is_verified", "type", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login",)}),
    )
    
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "phone_number", 
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_verified",
                    "type"
                ),
            },
        ),
    )

admin.site.register(User, UserAdminConfig)
admin.site.register(ProfileModel)
