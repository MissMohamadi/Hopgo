from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from .models import Book,Status


class LibrarySitemap(Sitemap):
    changefreq = "weekly"
    #priority = 0.8

    def items(self):
        return Book.objects.filter(status=Status.publish.value)

    def lastmod(self, obj):
        return obj.updated_date


''' always, hourly, daily, weekly, monthly, yearly, never '''
