"""Save as: website/admin.py  (if it already has admin classes, add these)"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from .models import AboutFact, AboutPage, HomePage, LegalPage


class FactInline(admin.TabularInline):
    model = AboutFact
    extra = 1
    fields = ("order", "label", "label_fa", "value", "value_fa")


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    inlines = [FactInline]
    fieldsets = (
        ("English", {"fields": ("title", "lead", "body")}),
        ("Persian (فارسی)", {"fields": ("title_fa", "lead_fa", "body_fa")}),
        ("Photo and contact", {"fields": ("photo", "email")}),
    )

    class Media:
        css = {"all": ("blogs/css/blog_content.css",)}

    # one page only: no "add" when it exists, no delete
    def has_add_permission(self, request):
        return not AboutPage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    # the list is useless with one row: go straight to the editor
    def changelist_view(self, request, extra_context=None):
        page = AboutPage.objects.first()
        if page:
            return redirect(reverse("admin:website_aboutpage_change", args=[page.pk]))
        return redirect(reverse("admin:website_aboutpage_add"))


"""ADD to  website/admin.py  (below the AboutPage admin). Add HomePage to the import line:
    from .models import AboutFact, AboutPage, HomePage
"""


@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Featured artwork (big picture)", {
         "fields": ("hero_painting", "hero_sculpture")}),
        ("English", {"fields": ("eyebrow", "headline", "lead", "quote")}),
        ("Persian (فارسی)", {"fields": ("eyebrow_fa",
         "headline_fa", "lead_fa", "quote_fa")}),
    )
    # (add "hero_painting", "hero_sculpture" if you set search_fields in shop admin)
    autocomplete_fields = ()
    raw_id_fields = ()

    def has_add_permission(self, request):
        return not HomePage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        page = HomePage.objects.first()
        if page:
            return redirect(reverse("admin:website_homepage_change", args=[page.pk]))
        return redirect(reverse("admin:website_homepage_add"))


"""ADD to  website/admin.py   and add LegalPage to the  `from .models import ...`  line."""


@admin.register(LegalPage)
class LegalPageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "updated_at")
    fieldsets = (
        ("English", {"fields": ("slug", "title", "body")}),
        ("Persian (فارسی)", {"fields": ("title_fa", "body_fa")}),
    )

    class Media:
        css = {"all": ("blogs/css/blog_content.css",)}
