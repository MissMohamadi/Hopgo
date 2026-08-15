from django.urls import path, include
from . import views


app_name = "dashboard"


urlpatterns = [
    # access dashboard
    path("home/",views.DashboardHomeView.as_view(),name="home"),
    
    # admin dashboard management
    path('admin/',include('dashboard.admin.urls')),
    
    # employee dashboard management
    path('customer/',include('dashboard.customer.urls')),
    
    
    
]
