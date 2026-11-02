"""Save as: website/admin.py  (if it already has admin classes, add these)"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from .models import AboutFact, AboutPage


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
