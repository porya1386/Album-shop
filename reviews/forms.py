import re

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Comment

LINK_RE = re.compile(r"https?://|www\.", re.IGNORECASE)
MAX_LINKS = 2


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("body",)
        labels = {"body": _("Your comment")}
        widgets = {
            "body": forms.Textarea(attrs={
                "rows": 3,
                "maxlength": 1000,
                "dir": "auto",
                "placeholder": _("Write your comment..."),
            }),
        }

    def clean_body(self):
        # Django already stripped the text and checked 3..1000 characters.
        body = self.cleaned_data["body"].replace("\r\n", "\n")
        body = re.sub(r"\n{3,}", "\n\n", body)          # no giant empty gaps
        if len(LINK_RE.findall(body)) > MAX_LINKS:
            raise forms.ValidationError(
                _("Please do not post more than two links."))
        return body
