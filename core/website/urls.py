from . import views
from django.urls import path, include, re_path

app_name = "website"

urlpatterns = [
    # render pages
    path("", views.IndexView.as_view(), name="index"),
    path("about-me/", views.AboutView.as_view(), name="about-me"),
    path("newsletter/", views.NewsletterView.as_view(), name="newsletter"),
    path("contact-me/", views.ContactView.as_view(), name="contact-me"),
    path("counseling-or-mentor/request/", views.CounselingOrMentorRequestView.as_view(),
         name="counseling-or-mentor-request"),
    path("project/request/", views.ProjectRequestView.as_view(),
         name="project-request"),
    path("road-map/security/", views.SecurityRoadMapView.as_view(),
         name="security-road-map"),
    path("policy-and-privacy/", views.PolicyAndPrivacyView.as_view(),
         name="policy-and-privacy"),




    # action posts
    path("submit/ticket", views.TicketView.as_view(), name="submit-ticket"),




    # path("musics", views.MusicListView.as_view(), name="music-list"),
    path("connect/", views.ConnectView.as_view(), name="connect"),



]
