from django.db import models
from django.urls import reverse
import os
from django.conf import settings


def get_domain():
    from django.contrib.sites.models import Site
    try:
        return Site.objects.get_current().domain
    except Site.DoesNotExist:
        return 'example.com'
    except:
        pass


def get_protocol():
    # Determine the protocol based on the SECURE_SSL_REDIRECT setting
    return 'https' if getattr(settings, 'SECURE_SSL_REDIRECT', False) else 'http'

def get_file_extension(filename):
    """Return the file extension of the given filename."""
    _, extension = os.path.splitext(filename)
    return extension.lower()

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    type = models.CharField(max_length=10, blank=True)
    name = models.CharField(max_length=255, blank=True)
    size = models.PositiveIntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def get_download_url(self):
        return f"{get_protocol()}://{get_domain()}{self.file.url}"
    

    def save(self, *args, **kwargs):
        # Set the extension field based on the uploaded file
        self.type = get_file_extension(self.file.name)
        self.name = os.path.basename(self.file.name)
        self.size = self.file.size
        super().save(*args, **kwargs)
    
    def get_size_display(self):
        """Return a human-readable representation of the file size."""
        if self.size < 1024:
            return '{} bytes'.format(self.size)
        elif self.size < 1024 * 1024:
            return '{:.1f} KB'.format(self.size / 1024)
        else:
            return '{:.1f} MB'.format(self.size / (1024 * 1024))
        
    def delete(self, *args, **kwargs):
        # Remove the file from the MEDIA_ROOT directory
        os.remove(os.path.join(settings.MEDIA_ROOT, self.file.name))
        super().delete(*args, **kwargs)