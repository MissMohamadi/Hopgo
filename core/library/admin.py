from django.contrib import admin
from .models import *


class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_date')
    list_filter = ("status", 'created_date')
    search_fields = ['title', 'content']

admin.site.register(Book, BookAdmin)
admin.site.register(BookCategory)
admin.site.register(BookTag)
