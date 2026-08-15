from django.urls import path, include, re_path

app_name = 'admin'

urlpatterns = [
    # generals urls
    path("", include("dashboard.admin.urls.generals")),
    # newsletters urls
    path("", include("dashboard.admin.urls.newsletters")),
    # users urls
    path("", include("dashboard.admin.urls.users")),
    # profiles urls
    path("", include("dashboard.admin.urls.profiles")),
    # contacts urls
    path("", include("dashboard.admin.urls.contacts")),
    # posts urls
    # path("", include("dashboard.admin.urls.posts")),
    # filehubs urls
    path("", include("dashboard.admin.urls.filehubs")),
    # library urls
    path("", include("dashboard.admin.urls.books")),
    # events urls

]
