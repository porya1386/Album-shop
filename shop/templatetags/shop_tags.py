"""Save as:  shop/templatetags/shop_tags.py   (replaces the old file)"""
from django import template
from django.urls import reverse

from shop.models import Album_image, Sculpture

register = template.Library()


@register.simple_tag
def latest_sculptures(limit=12):
    """{% latest_sculptures as sculptures %}  -> the newest sculptures (kept for old templates)."""
    return list(Sculpture.objects.order_by("-create_at", "-id")[:limit])


@register.simple_tag
def latest_works(limit=12):
    """{% latest_works as works %}  -> paintings AND sculptures mixed, newest first.

    Every item has:  url  image  title  price  kind ("painting" / "sculpture")
    """
    paintings = Album_image.objects.order_by("-create_at", "-id")[:limit]
    sculptures = Sculpture.objects.order_by("-create_at", "-id")[:limit]

    items = []
    for p in paintings:
        items.append((p.create_at, {
            "url": reverse("product_details", args=[p.slug]),
            "image": p.image.url if p.image else "",
            "title": p.display_title,
            "price": p.display_price,
            "kind": "painting",
        }))
    for s in sculptures:
        items.append((s.create_at, {
            "url": reverse("sculpture_details", args=[s.slug]),
            "image": s.image.url if s.image else "",
            "title": s.display_title,
            "price": s.display_price,
            "kind": "sculpture",
        }))

    items.sort(key=lambda pair: pair[0], reverse=True)
    return [data for _, data in items[:limit]]
