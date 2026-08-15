
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView

# from robots_txt.views import robots_txt
from website.sitemaps import StaticViewSitemap
from library.sitemaps import LibrarySitemap
from django.http import HttpResponse


sitemaps = {
    "static": StaticViewSitemap,    
    "library": LibrarySitemap,
}

def readiness_view(request):
    return HttpResponse("Ok", content_type="text/plain")

urlpatterns = [
    path("admin/", include("honeypot.urls")),
    path("secret-admin-entrance/", admin.site.urls),
        
    path("",include('website.urls')),    
    path("accounts/",include('accounts.urls', namespace='accounts')),
    path("dashboard/",include('dashboard.urls', namespace='dashboard')),
    path('library/', include('library.urls', namespace='library')),
    
    
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path("is-ready",readiness_view),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    # path('robots.txt', robots_txt, name='robots_txt'),  

    path('dog_walker/', include('DogWalker.urls.DogWalker', namespace = 'DogWalker')),
    path('dog_owner/', include('DogOwner.urls.DogOwner' , namespace="DogOwner")),

    
   
]

if settings.COMINGSOON:
    urlpatterns.insert(
        0, re_path(r"^", TemplateView.as_view(template_name="coming-soon.html"))
    )

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    

if settings.SHOW_DEBUGGER_TOOLBAR:
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls')),
                    ]


handler400 = "core.error_views.error_400"  # bad_request
handler403 = "core.error_views.error_403"  # permission_denied
handler404 = "core.error_views.error_404"  # page_not_found
handler500 = "core.error_views.error_500"  # server_error
