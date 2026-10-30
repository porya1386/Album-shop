from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class Comment(models.Model):
    """A text comment under a painting OR a sculpture. Published at once, no approval."""

    product = models.ForeignKey(
        "shop.Album_image",
        on_delete=models.CASCADE,
        related_name="comments",
        null=True,
        blank=True,
        verbose_name=_("painting"),
    )
    sculpture = models.ForeignKey(
        "shop.Sculpture",
        on_delete=models.CASCADE,
        related_name="comments",
        null=True,
        blank=True,
        verbose_name=_("sculpture"),
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
        indexes = [
            models.Index(fields=["product", "-created_at"]),
            models.Index(fields=["sculpture", "-created_at"]),
        ]
        constraints = [
            # a comment belongs to exactly ONE of them
            models.CheckConstraint(
                condition=(
                    Q(product__isnull=False, sculpture__isnull=True)
                    | Q(product__isnull=True, sculpture__isnull=False)
                ),
                name="comment_has_exactly_one_target",
            ),
        ]
        verbose_name = _("comment")
        verbose_name_plural = _("comments")

    @property
    def target(self):
        return self.product or self.sculpture

    def __str__(self):
        return f"{self.user} - {self.body[:40]}"
