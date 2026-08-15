from django import forms
from library.models import Book, Tag,BookCategory
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from dateutil import parser
from jdatetime import datetime as jdatetime
import json
from django.utils.text import slugify
from django.utils import timezone

class BookForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())
    tags = forms.CharField()

    class Meta:
        model = Book
        fields = [
            "title",
            "slug",
            "image",
            "image_alt",
            "pdf_file",
            "link_file",
            "content",
            "category",
            "tags",
            "status",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "slug": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "image_alt": forms.TextInput(attrs={"class": "form-control"}),
            "link_file": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }



    def clean_tags(self):
        tags = json.loads(self.cleaned_data.get("tags", None))
        if tags is None:
            return []
        return [item["value"] for item in tags]

    def clean_slug(self):
        slug_text = self.cleaned_data.get("slug")
        return slugify(slug_text, allow_unicode=True) if not slug_text else slug_text


    def clean(self):
        cleaned_data = super().clean()
        cleaned_data["tag"] = self.add_or_get_tags(cleaned_data.get("tags"))
        cleaned_data.pop("tags", None)
        return cleaned_data

    def add_or_get_tags(self, tags):
        if tags is None:
            return []
        result = []
        for tag_title in tags:
            tag_obj, _ = Tag.objects.get_or_create(title=tag_title, slug=slugify(tag_title, allow_unicode=True))
            result.append(tag_obj.pk)
        return result

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            instance.tag.set(self.cleaned_data["tag"])
            instance.save()
        return instance



class BookCategoryForm(forms.ModelForm):
    class Meta:
        model = BookCategory
        fields = ["title", "slug"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "slug": forms.TextInput(attrs={"class": "form-control"}),
        }