from dashboard.admin import views 
from django.urls import path,include


urlpatterns = [
    path("user/list", views.UserListView.as_view(), name="user-list"),
    path("user/<int:pk>/edit", views.UserEditView.as_view(), name="user-edit"),
    path("user/<int:pk>/delete", views.UserDeleteView.as_view(), name="user-delete"),
    path("user/<int:pk>/reset-password",views.UserResetPasswordView.as_view(),name="user-reset-password"),
    path("user/brief-list", views.UserBriefListView.as_view(), name="user-brief-list"),
]