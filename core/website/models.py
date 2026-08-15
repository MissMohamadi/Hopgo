from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.html import strip_spaces_between_tags, strip_tags
from django.utils.text import Truncator

from ckeditor_uploader.fields import RichTextUploadingField

from imagekit.models import ImageSpecField
from pilkit.processors import Thumbnail
from meta.models import ModelMeta
from django.utils.text import slugify

# fetching user model
User = get_user_model()

# defining the status of items to be saved or released

    
class TicketType(models.IntegerChoices):
    contact = 1
    mentor_or_counseling = 2
    project = 3
    online_course = 4
    


class Tag(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True,
                            allow_unicode=True, null=True)

    class Meta:
        verbose_name_plural = "tags"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)
        super(Tag, self).save(*args, **kwargs)


class Ticket(models.Model):

    full_name = models.CharField(max_length=200)
    email = models.EmailField(default=None, null=True)
    phone_number = models.CharField(max_length=200, blank=True, null=True)
    subject = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField(max_length=700)
    type = models.IntegerField(
        choices=TicketType.choices, default=TicketType.contact)
    is_seen = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return self.full_name

class NewsLetter(models.Model):
    email = models.EmailField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.email
    