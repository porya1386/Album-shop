"""Save as: website/templatetags/website_tags.py"""
from django import template

from ..models import AboutPage

register = template.Library()


@register.simple_tag
def about_page():
    """{% about_page as about %}  -> the AboutPage row (or None before it exists)."""
    return AboutPage.objects.prefetch_related("facts").first()
