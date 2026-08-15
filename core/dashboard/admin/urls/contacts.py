from dashboard.admin import views 
from django.urls import path,include


urlpatterns = [
    path("ticket/list", views.TicketListView.as_view(), name="ticket-list"),
    path("ticket/<int:pk>/detail", views.TicketDetailView.as_view(), name="ticket-detail"),
    path("ticket/<int:pk>/delete", views.TicketDeleteView.as_view(), name="ticket-delete"),
]