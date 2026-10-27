from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Album_image(models.Model):
    title = models.CharField(
        max_length=160,
        null=True,
        verbose_name=_("Album Image Title"),
        help_text=_("Enter your album image title"),
        blank=False,
        unique=True,
    )

    price = models.PositiveBigIntegerField(
        default=0,
        help_text=_("Enter your album image price"),
        verbose_name=_("Album Image Price"),
        blank=False,
    )

    description = models.TextField(
        blank=True,
        help_text=_("Enter the description for your album image"),
        verbose_name=_("Album Image Description"),
    )

    image = models.ImageField(
        verbose_name=_("Album Image"),
        help_text=_("Upload your image"),
        upload_to="shop/album_image",
    )

    slug = models.SlugField(
        blank=False,
        null=True,
        verbose_name=_("Slug"),
    )

    size = models.CharField(
        blank=False,
        null=True,
        help_text=_("Enter your album image size, e.g. 60 x 90 cm"),
        verbose_name=_("Album Image Size"),
    )

    year = models.DateField(
        null=True,
        verbose_name=_("Album Image Creation Date"),
        help_text=_("Enter the date you created this masterpiece"),
    )

    create_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
    )

    update_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Available for Sale"),
        help_text=_("Indicates whether this album image is available for sale"),
    )

    views = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name=_("Views"),
    )

    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="liked_paintings",
        blank=True,
        verbose_name=_("Liked By"),
    )

    class Meta:
        verbose_name = _("Album Image")
        verbose_name_plural = _("Album Images")

    def __str__(self):
        return f"{self.title} {self.is_active} {self.price}"

    def save(self, *args, **kwargs):
        if self.title:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Album_image_gallery(models.Model):
    product = models.ForeignKey(
        Album_image,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Product"),
    )

    image = models.ImageField(
        upload_to="shop/album_gallery",
        verbose_name=_("Gallery Image"),
    )

    caption = models.CharField(
        max_length=160,
        blank=True,
        verbose_name=_("Caption"),
    )

    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Display Order"),
    )

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("Album Image Gallery")
        verbose_name_plural = _("Album Image Galleries")

    def __str__(self):
        return f"{self.product.title} #{self.order}"
