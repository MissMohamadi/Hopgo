from django.urls import path
from .. import views

app_name = "DogWalker"

urlpatterns= [
    path('index', views.DogWalker_view.as_view(), name='index')
]