from dashboard.admin import views 
from django.urls import path,include


urlpatterns = [
    path("filehub/list", views.FileHubListView.as_view(), name="filehub-list"),
    path("filehub/create", views.FileHubCreateView.as_view(), name="filehub-create"),
    path("filehub/<int:pk>/delete", views.FileHubDeleteView.as_view(), name="filehub-delete"),
]