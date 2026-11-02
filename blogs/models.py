from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

MAX_COVER_MB = 5


def _is_fa():
    return (get_language() or "").startswith("fa")


def validate_cover(file):
    if file.size > MAX_COVER_MB * 1024 * 1024:
        raise ValidationError(_("The image must be smaller than %(mb)s MB.") % {"mb": MAX_COVER_MB})


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=Post.PUBLISHED, published_at__lte=timezone.now())


class Post(models.Model):
    """Posts are written ONLY in the admin panel. The site just shows the published ones."""

    DRAFT, PUBLISHED = "draft", "published"
    STATUS_CHOICES = [(DRAFT, _("Draft")), (PUBLISHED, _("Published"))]

    title = models.CharField(_("Title"), max_length=200)
    slug = models.SlugField(_("Slug"), max_length=220, unique=True, allow_unicode=True, blank=True,
                            help_text=_("Leave empty: it is made from the title."))
    cover = models.ImageField(_("Cover image"), upload_to="blogs/covers", blank=True,
                              validators=[validate_cover])
    excerpt = models.CharField(_("Short summary"), max_length=300, blank=True)
    body = models.TextField(_("Text"))

    # Persian version (shown on /fa/ ; when empty the English one is shown)
    title_fa = models.CharField(_("Persian title"), max_length=200, blank=True,
                                help_text=_("Title shown on the Persian site. Leave empty to use the English title."))
    excerpt_fa = models.CharField(_("Persian short summary"), max_length=300, blank=True)
    body_fa = models.TextField(_("Persian text"), blank=True,
                               help_text=_("Text shown on the Persian site. Leave empty to use the English text."))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name="blog_posts",
                               verbose_name=_("Author"))
    status = models.CharField(_("Status"), max_length=10, choices=STATUS_CHOICES, default=DRAFT)
    published_at = models.DateTimeField(_("Published at"), null=True, blank=True)

    views = models.PositiveIntegerField(_("Views"), default=0, editable=False)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="liked_posts",
                                   blank=True, verbose_name=_("Likes"))

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

    # what the visitor sees, by the language of the page
    @property
    def display_title(self):
        return self.title_fa if _is_fa() and self.title_fa else self.title

    @property
    def display_excerpt(self):
        return self.excerpt_fa if _is_fa() and self.excerpt_fa else self.excerpt

    @property
    def display_body(self):
        return self.body_fa if _is_fa() and self.body_fa else self.body

    @property
    def is_live(self):
        return bool(self.status == self.PUBLISHED and self.published_at and self.published_at <= timezone.now())

    def _make_slug(self):
        base = slugify(self.title, allow_unicode=True)[:200] or "post"
        if base in {"comment"}:
            base += "-post"
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


class PostComment(models.Model):
    """A text comment under a post. Published at once; the author or a moderator can delete it."""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="blog_comments")
    body = models.CharField(_("comment"), max_length=1000, validators=[MinLengthValidator(3)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")

    def __str__(self):
        return f"{self.user} - {self.body[:40]}"


class PostImage(models.Model):
    """A picture that can be placed INSIDE the text: write  [image 1]  on its own line in the post text."""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")
    order = models.PositiveSmallIntegerField(
        _("Number"), default=0,
        help_text=_("Write [image NUMBER] on its own line in the text where the picture should appear."))
    image = models.ImageField(_("Image"), upload_to="blogs/images", validators=[validate_cover])
    caption = models.CharField(_("Caption"), max_length=200, blank=True)
    caption_fa = models.CharField(_("Persian caption"), max_length=200, blank=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("Image in text")
        verbose_name_plural = _("Images in text")

    def __str__(self):
        return f"[image {self.order}] {self.caption}".strip()

    @property
    def display_caption(self):
        return self.caption_fa if _is_fa() and self.caption_fa else self.caption

    def save(self, *args, **kwargs):
        if not self.order:
            last = PostImage.objects.filter(post=self.post).aggregate(m=models.Max("order"))["m"] or 0
            self.order = last + 1
        super().save(*args, **kwargs)
