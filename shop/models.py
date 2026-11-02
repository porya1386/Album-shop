from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field

PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

# ---- video upload rules (change MAX_VIDEO_MB if you want a bigger limit) ----
MAX_VIDEO_MB = 100
VIDEO_EXTENSIONS = ["mp4", "webm", "mov", "m4v"]


def validate_video_size(file):
    if file.size > MAX_VIDEO_MB * 1024 * 1024:
        raise ValidationError(
            _("The video is too big. The maximum size is %(mb)s MB."),
            params={"mb": MAX_VIDEO_MB},
        )


# 16 base colours the admin can choose from (up to 4 per painting)
COLOR_CHOICES = [
    ("red", _("Red")),
    ("orange", _("Orange")),
    ("yellow", _("Yellow")),
    ("lime", _("Lime")),
    ("green", _("Green")),
    ("teal", _("Teal")),
    ("cyan", _("Cyan")),
    ("blue", _("Blue")),
    ("navy", _("Navy")),
    ("purple", _("Purple")),
    ("pink", _("Pink")),
    ("brown", _("Brown")),
    ("beige", _("Beige")),
    ("gray", _("Gray")),
    ("black", _("Black")),
    ("white", _("White")),
]

COLOR_HEX = {
    "red": "#D32F2F", "orange": "#F57C00", "yellow": "#FBC02D", "lime": "#AFB42B",
    "green": "#388E3C", "teal": "#00897B", "cyan": "#00ACC1", "blue": "#1976D2",
    "navy": "#1A237E", "purple": "#7B1FA2", "pink": "#EC407A", "brown": "#6D4C41",
    "beige": "#D7C4A3", "gray": "#757575", "black": "#111111", "white": "#F5F5F5",
}


class LocalizedMixin:
    """display_title / display_description / display_price for paintings AND sculptures.
    In Farsi the *_fa fields are used when they are filled, otherwise the English ones."""

    @staticmethod
    def _is_fa():
        return (get_language() or "").startswith("fa")

    @property
    def display_title(self):
        return self.title_fa if self._is_fa() and self.title_fa else self.title

    @property
    def display_description(self):
        return self.description_fa if self._is_fa() and self.description_fa else self.description

    @property
    def display_price(self):
        if self._is_fa() and self.price_toman:
            return f"{self.price_toman:,}".replace(",", "٬").translate(PERSIAN_DIGITS) + " تومان"
        text = f"{self.price:,.2f}"
        if text.endswith(".00"):
            text = text[:-3]
        return f"${text}"


class Album_image(LocalizedMixin, models.Model):
    # Persian version (shown only when the site language is Farsi)
    title_fa = models.CharField(
        max_length=160,
        blank=True,
        verbose_name=_("Persian title"),
        help_text=_(
            "Title shown on the Persian site. Leave empty to use the English title."),
    )

    description_fa = CKEditor5Field(
        config_name="persian",
        blank=True,
        verbose_name=_("Persian description"),
        help_text=_(
            "Description shown on the Persian site. Leave empty to use the English one."),
    )

    price_toman = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Price (Toman)"),
        help_text=_(
            "Price shown on the Persian site, in Toman. Leave empty to show the normal price."),
    )

    title = models.CharField(
        max_length=160,
        null=True,
        verbose_name=_("Album Image Title"),
        help_text=_("Enter your album image title"),
        blank=False,
        unique=True,
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0"))],
        blank=False,
        help_text=_("Enter your album image price"),
        verbose_name=_("Album Image Price"),
    )

    description = CKEditor5Field(
        config_name="default",
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

    # up to 4 main colours of the painting (picked in the admin)
    color_1 = models.CharField(max_length=10, choices=COLOR_CHOICES,
                               blank=True, verbose_name=_("Colour 1"))
    color_2 = models.CharField(max_length=10, choices=COLOR_CHOICES,
                               blank=True, verbose_name=_("Colour 2"))
    color_3 = models.CharField(max_length=10, choices=COLOR_CHOICES,
                               blank=True, verbose_name=_("Colour 3"))
    color_4 = models.CharField(max_length=10, choices=COLOR_CHOICES,
                               blank=True, verbose_name=_("Colour 4"))

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

    @property
    def color_list(self):
        """Chosen colours (no empty ones, no duplicates) as [{"hex": ..., "name": ...}]."""
        names = dict(COLOR_CHOICES)
        seen, out = set(), []
        for code in (self.color_1, self.color_2, self.color_3, self.color_4):
            if code and code in COLOR_HEX and code not in seen:
                seen.add(code)
                out.append({"hex": COLOR_HEX[code], "name": names[code]})
        return out

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
        blank=True,
        verbose_name=_("Gallery Image"),
    )

    video = models.FileField(
        upload_to="shop/album_gallery_video",
        blank=True,
        validators=[FileExtensionValidator(
            VIDEO_EXTENSIONS), validate_video_size],
        verbose_name=_("Video"),
        help_text=_("Upload an image OR a video (MP4 or WebM, up to 100 MB)."),
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

    def clean(self):
        # exactly one of image / video
        if bool(self.image) == bool(self.video):
            raise ValidationError(
                _("Upload either an image or a video (not both, not empty)."))

    @property
    def is_video(self):
        return bool(self.video)

    def __str__(self):
        return f"{self.product.title} #{self.order}"


MATERIAL_CHOICES = [
    ("bronze", _("Bronze")),
    ("marble", _("Marble")),
    ("stone", _("Stone")),
    ("wood", _("Wood")),
    ("ceramic", _("Ceramic")),
    ("metal", _("Metal")),
    ("glass", _("Glass")),
    ("resin", _("Resin")),
    ("mixed", _("Mixed media")),
    ("other", _("Other")),
]


class Sculpture(LocalizedMixin, models.Model):
    """A sculpture. It has its own list (Products page -> Sculptures tab) and its own details page."""

    title = models.CharField(
        max_length=160,
        unique=True,
        verbose_name=_("Sculpture Title"),
        help_text=_("Enter your sculpture title"),
    )

    title_fa = models.CharField(
        max_length=160,
        blank=True,
        verbose_name=_("Persian title"),
        help_text=_(
            "Title shown on the Persian site. Leave empty to use the English title."),
    )

    slug = models.SlugField(blank=True, verbose_name=_("Slug"))

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0"))],
        help_text=_("Enter your sculpture price"),
        verbose_name=_("Sculpture Price"),
    )

    price_toman = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Price (Toman)"),
        help_text=_(
            "Price shown on the Persian site, in Toman. Leave empty to show the normal price."),
    )

    description = CKEditor5Field(
        config_name="default",
        blank=True,
        help_text=_("Enter the description for your sculpture"),
        verbose_name=_("Sculpture Description"),
    )

    description_fa = CKEditor5Field(
        config_name="persian",
        blank=True,
        verbose_name=_("Persian description"),
        help_text=_(
            "Description shown on the Persian site. Leave empty to use the English one."),
    )

    image = models.ImageField(
        verbose_name=_("Sculpture Image"),
        help_text=_("Upload your image"),
        upload_to="shop/sculpture",
    )

    material = models.CharField(
        max_length=10,
        choices=MATERIAL_CHOICES,
        blank=True,
        verbose_name=_("Material"),
    )

    size = models.CharField(
        max_length=80,
        blank=True,
        verbose_name=_("Sculpture Size"),
        help_text=_("Enter the size, e.g. H 40 x W 20 x D 15 cm"),
    )

    weight_kg = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name=_("Weight (kg)"),
    )

    year = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Year"),
        help_text=_("The year you made it, e.g. 2024"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Available for Sale"),
        help_text=_("Indicates whether this sculpture is available for sale"),
    )

    views = models.PositiveIntegerField(
        default=0, editable=False, verbose_name=_("Views"))

    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="liked_sculptures",
        blank=True,
        verbose_name=_("Liked By"),
    )

    create_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At"))
    update_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Sculpture")
        verbose_name_plural = _("Sculptures")

    def __str__(self):
        return f"{self.title} {self.is_active} {self.price}"

    @property
    def material_label(self):
        return dict(MATERIAL_CHOICES).get(self.material, "")

    def save(self, *args, **kwargs):
        if self.title:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Sculpture_gallery(models.Model):
    sculpture = models.ForeignKey(
        Sculpture,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Sculpture"),
    )
    image = models.ImageField(
        upload_to="shop/sculpture_gallery", blank=True,
        verbose_name=_("Gallery Image"))
    video = models.FileField(
        upload_to="shop/sculpture_gallery_video",
        blank=True,
        validators=[FileExtensionValidator(
            VIDEO_EXTENSIONS), validate_video_size],
        verbose_name=_("Video"),
        help_text=_("Upload an image OR a video (MP4 or WebM, up to 100 MB)."),
    )
    caption = models.CharField(
        max_length=160, blank=True, verbose_name=_("Caption"))
    order = models.PositiveSmallIntegerField(
        default=0, verbose_name=_("Display Order"))

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("Sculpture Gallery")
        verbose_name_plural = _("Sculpture Galleries")

    def clean(self):
        # exactly one of image / video
        if bool(self.image) == bool(self.video):
            raise ValidationError(
                _("Upload either an image or a video (not both, not empty)."))

    @property
    def is_video(self):
        return bool(self.video)

    def __str__(self):
        return f"{self.sculpture.title} #{self.order}"
