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
