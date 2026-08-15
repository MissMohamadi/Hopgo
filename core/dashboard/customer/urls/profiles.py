from dashboard.customer import views
from django.urls import path,include


urlpatterns = [
    # profiles control pages
    path("profile/edit", views.ProfileEditView.as_view(), name="profile-edit"),
    path("profile/avatar-edit", views.ProfileAvatarEditView.as_view(), name="avatar-edit"),
    path("profile/password-edit", views.ProfilePasswordEditView.as_view(), name="password-edit"),
]