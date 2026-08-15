from . import views
from django.urls import path,re_path

app_name = "library"

urlpatterns = [
    path('', views.BookListView.as_view(), name='book-list'),
    re_path(r'^(?P<slug>[-\w]+)/$',views.BookDetailView.as_view(), name='book-detail'),
    
]
