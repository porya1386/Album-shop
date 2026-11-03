"""Save as: website/templatetags/website_tags.py"""
from ..models import AboutPage, HomePage
from django.urls import reverse
from django import template

from ..models import AboutPage

register = template.Library()


@register.simple_tag
def about_page():
    """{% about_page as about %}  -> the AboutPage row (or None before it exists)."""
    return AboutPage.objects.prefetch_related("facts").first()


"""Save as: website/templatetags/website_tags.py   (replaces the old file, keeps about_page)"""


register = template.Library()


@register.simple_tag
def about_page():
    """{% about_page as about %}  -> the AboutPage row (or None before it exists)."""
    return AboutPage.objects.prefetch_related("facts").first()


@register.simple_tag
def home_page():
    """{% home_page as hp %}  -> the HomePage row (or None before it exists)."""
    return HomePage.objects.select_related("hero_painting", "hero_sculpture").first()


def _painting(p):
    return {"url": reverse("product_details", args=[p.slug]), "image": p.image.url if p.image else "",
            "title": p.display_title, "price": p.display_price, "kind": "painting",
            "year": p.year.year if getattr(p, "year", None) else ""}


def _sculpture(s):
    return {"url": reverse("sculpture_details", args=[s.slug]), "image": s.image.url if s.image else "",
            "title": s.display_title, "price": s.display_price, "kind": "sculpture",
            "year": s.year or ""}


@register.simple_tag
def home_hero():
    """{% home_hero as hero %}  -> the featured artwork chosen in the admin (or the newest painting)."""
    from shop.models import Album_image
    hp = HomePage.objects.select_related(
        "hero_painting", "hero_sculpture").first()
    if hp:
        if hp.hero_painting_id and hp.hero_painting.image:
            return _painting(hp.hero_painting)
        if hp.hero_sculpture_id and hp.hero_sculpture.image:
            return _sculpture(hp.hero_sculpture)
    p = Album_image.objects.exclude(
        image="").order_by("-create_at", "-id").first()
    return _painting(p) if p else None


@register.simple_tag
def home_works(limit=4):
    """{% home_works 4 as works %} -> newest paintings+sculptures mixed, each with year and a short plain text."""
    from django.utils.html import strip_tags
    from django.utils.text import Truncator
    from shop.models import Album_image, Sculpture
    rows = []
    for p in Album_image.objects.exclude(image="").order_by("-create_at", "-id")[:limit]:
        d = _painting(p)
        d["text"] = Truncator(strip_tags(
            p.display_description or "")).words(26)
        rows.append((p.create_at, d))
    for sc in Sculpture.objects.exclude(image="").order_by("-create_at", "-id")[:limit]:
        d = _sculpture(sc)
        d["text"] = Truncator(strip_tags(
            sc.display_description or "")).words(26)
        rows.append((sc.create_at, d))
    rows.sort(key=lambda r: r[0], reverse=True)
    out = [d for _, d in rows[:limit]]
    for i, d in enumerate(out, 1):
        d["n"] = i
    return out


@register.simple_tag
def site_counts():
    """{% site_counts as n %}  -> n.paintings  n.sculptures  n.posts"""
    from blogs.models import Post
    from shop.models import Album_image, Sculpture
    return {"paintings": Album_image.objects.count(), "sculptures": Sculpture.objects.count(),
            "posts": Post.objects.published().count()}
