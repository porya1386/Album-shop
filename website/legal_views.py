"""Save as  website/legal_views.py"""
from django.shortcuts import get_object_or_404, render

from .models import LegalPage


def legal_page(request, slug):
    page = get_object_or_404(LegalPage, slug=slug)
    return render(request, "website/legal_page.html", {"page": page, "all_pages": LegalPage.objects.all()})
