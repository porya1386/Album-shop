from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Comment(models.Model):
    """A text comment under a painting. Published at once, no approval."""

    product = models.ForeignKey(
        "shop.Album_image",
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("painting"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("user"),
    )
    body = models.CharField(
        _("comment"),
        max_length=1000,
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["product", "-created_at"])]
        verbose_name = _("comment")
        verbose_name_plural = _("comments")

    def __str__(self):
        return f"{self.user} - {self.body[:40]}"
