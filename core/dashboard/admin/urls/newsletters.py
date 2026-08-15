from dashboard.admin import views 
from django.urls import path,include


urlpatterns = [
    path("newsletter/list", views.NewsletterListView.as_view(), name="newsletter-list"),
    path("newsletter/<int:pk>/delete", views.NewsletterDeleteView.as_view(), name="newsletter-delete"),
]