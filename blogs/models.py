from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

MAX_COVER_MB = 5


def validate_cover(file):
    if file.size > MAX_COVER_MB * 1024 * 1024:
        raise ValidationError(_("The image must be smaller than %(mb)s MB.") % {"mb": MAX_COVER_MB})


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=Post.PUBLISHED, published_at__lte=timezone.now())


class Post(models.Model):
    DRAFT, PUBLISHED = "draft", "published"
    STATUS_CHOICES = [(DRAFT, _("Draft")), (PUBLISHED, _("Published"))]

    title = models.CharField(_("Title"), max_length=200)
    slug = models.SlugField(_("Slug"), max_length=220, unique=True, allow_unicode=True, blank=True,
                            help_text=_("Leave empty: it is made from the title."))
    cover = models.ImageField(_("Cover image"), upload_to="blogs/covers", blank=True,
                              validators=[validate_cover])
    excerpt = models.CharField(_("Short summary"), max_length=300, blank=True)
    body = models.TextField(_("Text"))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name="blog_posts",
                               verbose_name=_("Author"))
    status = models.CharField(_("Status"), max_length=10, choices=STATUS_CHOICES, default=DRAFT)
    published_at = models.DateTimeField(_("Published at"), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blogs:detail", kwargs={"slug": self.slug})

    @property
    def is_live(self):
        return self.status == self.PUBLISHED and self.published_at and self.published_at <= timezone.now()

    def _make_slug(self):
        base = slugify(self.title, allow_unicode=True)[:200] or "post"
        if base == "new":
            base = "new-post"          # "new" is the create page
        slug, n = base, 2
        while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base}-{n}"
            n += 1
        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._make_slug()
        if self.status == self.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
