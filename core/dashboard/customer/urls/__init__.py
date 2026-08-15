from django.urls import path, include, re_path

app_name = 'customer'

urlpatterns = [
    # general urls
    path("", include("dashboard.customer.urls.generals")),
    
    # profile urls
    path("", include("dashboard.customer.urls.profiles")),    

]
