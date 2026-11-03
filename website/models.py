"""About page that the site owner can edit in the admin panel.

There is ONE AboutPage row (a "singleton"). Facts ("Based in", "Languages" ...) are small rows under it.
Save as: website/models.py   (if the file already has models, keep them and add these two classes + the imports)
"""
from django.db import models
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field


def _is_fa():
    return (get_language() or "").startswith("fa")


class AboutPage(models.Model):
    title = models.CharField(
        _("Page title"), max_length=120, default="About me")
    title_fa = models.CharField(
        _("Persian page title"), max_length=120, blank=True, default="درباره من")

    lead = models.CharField(_("Short intro"), max_length=300, blank=True,
                            help_text=_("One sentence under the page title."))
    lead_fa = models.CharField(
        _("Persian short intro"), max_length=300, blank=True)

    body = CKEditor5Field(_("Text"), config_name="default", blank=True)
    body_fa = CKEditor5Field(_("Persian text"), config_name="persian", blank=True,
                             help_text=_("Text shown on the Persian site. Leave empty to use the English text."))

    photo = models.ImageField(
        _("Photo"), upload_to="website/about", blank=True)
    email = models.EmailField(_("Email"), blank=True,
                              help_text=_("Shown in the \"At a glance\" box and on the Email me button."))

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("About page")
        verbose_name_plural = _("About page")

    def __str__(self):
        return "About page"

    def save(self, *args, **kwargs):
        self.pk = 1                     # always the same single row
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass                            # it cannot be deleted by mistake

    @property
    def display_title(self):
        return self.title_fa if _is_fa() and self.title_fa else self.title

    @property
    def display_lead(self):
        return self.lead_fa if _is_fa() and self.lead_fa else self.lead

    @property
    def display_body(self):
        return self.body_fa if _is_fa() and self.body_fa else self.body


class AboutFact(models.Model):
    """One line of the "At a glance" box, e.g.  Based in -> Tehran, Iran."""

    about = models.ForeignKey(
        AboutPage, on_delete=models.CASCADE, related_name="facts")
    label = models.CharField(_("Label"), max_length=80)
    label_fa = models.CharField(_("Persian label"), max_length=80, blank=True)
    value = models.CharField(_("Value"), max_length=200)
    value_fa = models.CharField(_("Persian value"), max_length=200, blank=True)
    order = models.PositiveSmallIntegerField(_("Order"), default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("Fact")
        verbose_name_plural = _("Facts (At a glance)")

    def __str__(self):
        return self.label

    @property
    def display_label(self):
        return self.label_fa if _is_fa() and self.label_fa else self.label

    @property
    def display_value(self):
        return self.value_fa if _is_fa() and self.value_fa else self.value


class HomePage(models.Model):
    """Texts and the featured artwork of the home page. ONE row only (edited in the admin)."""

    # the big artwork next to the headline: choose a painting OR a sculpture
    hero_painting = models.ForeignKey(
        "shop.Album_image", verbose_name=_("Featured painting"), null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        help_text=_("The big picture on the home page. Choose a painting OR a sculpture. "
                    "If both are empty the newest painting is shown."))
    hero_sculpture = models.ForeignKey(
        "shop.Sculpture", verbose_name=_("Featured sculpture"), null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+")

    eyebrow = models.CharField(_("Small line above the title"), max_length=80, blank=True,
                               default="Art gallery")
    eyebrow_fa = models.CharField(
        _("Persian small line"), max_length=80, blank=True, default="گالری هنری")
    headline = models.CharField(
        _("Big title"), max_length=160, default="Quiet places, careful work.")
    headline_fa = models.CharField(
        _("Persian big title"), max_length=160, blank=True)
    lead = models.CharField(
        _("Short text under the title"), max_length=300, blank=True)
    lead_fa = models.CharField(
        _("Persian short text"), max_length=300, blank=True)

    quote = models.CharField(_("Quote of the artist"), max_length=300, blank=True,
                             help_text=_("A sentence shown big next to the artist photo."))
    quote_fa = models.CharField(_("Persian quote"), max_length=300, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Home page")
        verbose_name_plural = _("Home page")

    def __str__(self):
        return "Home page"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @staticmethod
    def _fa():
        from django.utils.translation import get_language
        return (get_language() or "").startswith("fa")

    def _pick(self, en, fa):
        return fa if self._fa() and fa else en

    @property
    def display_eyebrow(self):
        return self._pick(self.eyebrow, self.eyebrow_fa)

    @property
    def display_headline(self):
        return self._pick(self.headline, self.headline_fa)

    @property
    def display_lead(self):
        return self._pick(self.lead, self.lead_fa)

    @property
    def display_quote(self):
        return self._pick(self.quote, self.quote_fa)


"""ADD to  website/models.py  (at the bottom). Needs at the top:
    from django.db import models
    from django.utils.translation import get_language, gettext_lazy as _
    from django_ckeditor_5.fields import CKEditor5Field
"""


class LegalPage(models.Model):
    """Terms of service, privacy policy, cookie policy, shipping & returns. Edited in the admin (EN + FA)."""

    TERMS, PRIVACY, COOKIES, SHIPPING = "terms", "privacy", "cookies", "shipping-returns"
    SLUGS = [
        (TERMS, _("Terms of Service")),
        (PRIVACY, _("Privacy Policy")),
        (COOKIES, _("Cookie Policy")),
        (SHIPPING, _("Shipping & Returns")),
    ]

    slug = models.SlugField(_("Page"), max_length=40,
                            unique=True, choices=SLUGS)
    title = models.CharField(_("Title"), max_length=120)
    title_fa = models.CharField(_("Persian title"), max_length=120, blank=True)
    body = CKEditor5Field(_("Text"), config_name="default", blank=True)
    body_fa = CKEditor5Field(_("Persian text"), config_name="persian", blank=True,
                             help_text=_("Leave empty to show the English text."))
    updated_at = models.DateTimeField(_("Last updated"), auto_now=True)

    class Meta:
        ordering = ["slug"]
        verbose_name = _("Legal page")
        verbose_name_plural = _("Legal pages")

    def __str__(self):
        return self.title

    @staticmethod
    def _fa():
        return (get_language() or "").startswith("fa")

    @property
    def display_title(self):
        return self.title_fa if self._fa() and self.title_fa else self.title

    @property
    def display_body(self):
        return self.body_fa if self._fa() and self.body_fa else self.body
