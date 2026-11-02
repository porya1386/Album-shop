from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "cover", "excerpt", "body", "status")
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": _("Post title")}),
            "excerpt": forms.TextInput(attrs={"placeholder": _("One or two sentences for the list page")}),
            "body": forms.Textarea(attrs={"rows": 16}),
            "cover": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }
