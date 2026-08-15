from django.contrib import admin
from .models import User, ProfileModel,SocialProfileModel
from django.contrib.auth.admin import UserAdmin



class UserAdminConfig(UserAdmin):
    model = User
    search_fields = ("national_id",)
    list_filter = ("national_id", "username","is_active", "is_staff")
    ordering = ("-created_date",)
    list_display = ("national_id", "is_active", "is_staff","is_verified")
    fieldsets = (
        ("Authentication", {"fields": ("national_id","password","username")}),
        ("Permissions", {"fields": ("is_staff", "is_active","is_verified","type")}),
        (
            "Group Permissions",
            {
                "fields": (
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "national_id",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_verified"
                ),
            },
        ),
    )
    


    

admin.site.register(User, UserAdminConfig)
admin.site.register(ProfileModel)

