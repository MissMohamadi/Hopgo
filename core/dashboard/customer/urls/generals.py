from dashboard.customer import views
from django.urls import path,include


urlpatterns = [
    # render pages
    path("", views.DashboardHomeView.as_view(), name="home"),
    

]