from django.urls import path
from .. import views

app_name = 'DogOwner'

urlpatterns= [
    path('index', views.DogOwner_view.as_view(), name='index')
]