from django import template

from shop.models import Sculpture

register = template.Library()


@register.simple_tag
def latest_sculptures(limit=12):
    """{% latest_sculptures as sculptures %}  -> the newest sculptures (for the home page)."""
    return list(Sculpture.objects.order_by("-create_at", "-id")[:limit])
