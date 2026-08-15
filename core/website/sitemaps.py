from django.contrib import sitemaps
from django.urls import reverse


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return [
            'index',
                'about-me',
                'contact-me',                
                'counseling-or-mentor-request',
                'project-request',
                'security-road-map',
                'policy-and-privacy',
                'python-roadmap',
                'website-roadmap',
                'service-roadmap',
                'microservice-roadmap',                                
                'connect',                                
                
                ]

    def location(self, item):
        return reverse(f"website:{item}")
