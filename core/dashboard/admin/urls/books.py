from dashboard.admin import views 
from django.urls import path,include


urlpatterns = [
    path("book/list", views.BookListView.as_view(), name="book-list"),
    path("book/create", views.BookCreateView.as_view(), name="book-create"),
    path("book/<int:pk>/detail", views.BookDetailView.as_view(), name="book-detail"),
    path("book/<int:pk>/edit", views.BookEditView.as_view(), name="book-edit"),
    path("book/<int:pk>/delete", views.BookDeleteView.as_view(), name="book-delete"),
    path("book/category/list", views.BookCategoryListView.as_view(), name="book-category-list"),
    path("book/category/create", views.BookCategoryCreateView.as_view(), name="book-category-create"),
    path("book/category/<int:pk>/edit", views.BookCategoryEditView.as_view(), name="book-category-edit"),
    path("book/category/<int:pk>/delete", views.BookCategoryDeleteView.as_view(), name="book-category-delete"),
]