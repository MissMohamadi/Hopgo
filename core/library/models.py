from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

from django.utils import timezone
from django.db.models import Q
from django.utils.html import strip_spaces_between_tags, strip_tags
from django.utils.text import Truncator
from meta.models import ModelMeta
from ckeditor_uploader.fields import RichTextUploadingField
from pilkit.processors import Thumbnail
from imagekit.models import ImageSpecField
from website.models import Tag
from django.utils.text import slugify
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save


User = get_user_model()


class Status(models.IntegerChoices):
    publish = 1, "انتشار"
    draft = 2, "ذخیره"




class BookCategory(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True,
                            allow_unicode=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "categories"
        verbose_name = 'category'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)
        super(BookCategory, self).save(*args, **kwargs)


class BookTag(Tag):
    class Meta:
        proxy = True
        managed = False


class Book(ModelMeta, models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True,
                            allow_unicode=True, null=True, blank=True)
    image = models.ImageField(
        upload_to='images/book_thumbs', default='images/book_thumbs/default.png')
    image_alt = models.CharField(max_length=200, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    link_file = models.URLField(null=True, blank=True)
    pdf_file = models.FileField(upload_to="books/", null=True, blank=True)
    content = RichTextUploadingField()
    category = models.ForeignKey(
        BookCategory, on_delete=models.SET_NULL, null=True)
    tag = models.ManyToManyField(BookTag)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    status = models.IntegerField(
        choices=Status.choices, default=Status.draft.value)
    views = models.IntegerField(default=0)



    image_large = ImageSpecField(source='image',
                                 processors=[Thumbnail(391, 507)],
                                 format='WEBP',
                                 options={'quality': 60})
    image_medium = ImageSpecField(source='image',
                                  processors=[Thumbnail(298, 386)],
                                  format='WEBP',
                                  options={'quality': 60})
    image_small = ImageSpecField(source='image',
                                 processors=[Thumbnail(60, 78)],
                                 format='WEBP',
                                 options={'quality': 60})

    _metadata = {
        'title': 'title',
        'description': 'get_meta_description',
        'image': 'get_meta_image',
        'published_time': 'published_date',
        'modified_time': 'updated_date',
        'url': 'get_absolute_url',
        'locale': 'fa_IR',
        'keywords': 'get_meta_keywords',
        'twitter_title':'title',
        'twitter_description':'get_meta_description',
        'twitter_type':'get_meta_description'
    }

    def get_meta_description(self):
        value = strip_spaces_between_tags(self.content)
        value = value.replace("</p>", " </p>")
        value = value.replace("&quot", "  ")
        value = strip_tags(value)
        return Truncator(value).words(40)

    def get_meta_image(self):
        if self.image:
            return self.image.url

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return self.title

    def snippet(self):
        return self.content[:100]+" ..."

    def get_meta_keywords(self):
        return [tag_obj.title for tag_obj in self.tag.all()]

    def get_absolute_url(self):
        return reverse("library:book-detail", kwargs={"slug": self.slug})

    def get_file_url(self):
        if self.link_file is not None:
            return self.link_file
        elif self.pdf_file is not None:
            return self.pdf_file.url
        else:
            "#"

    @property
    def is_published(self):
        return True if self.status == Status.publish.value else False

    def save(self, *args, **kwargs):
        if not self.slug:
            # If the slug field is empty, generate a slug from the title
            self.slug = slugify(self.title, allow_unicode=True)
        super(Book, self).save(*args, **kwargs)



