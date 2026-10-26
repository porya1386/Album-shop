from django.db.models import Count, Exists, F, OuterRef, Q, Value, BooleanField
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_POST, require_safe
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import ProductFilterForm
from .models import Album_image
from .search import parse_terms
from .serializer import Album_Serializer


# ---------------------------------------------------------------- helpers

def _search_q(terms):
    """Every word must match the title, the price or the year."""
    q = Q()
    for term in terms:
        match = Q(title__icontains=term["text"])
        if term["number"] is not None:
            match |= Q(price=term["number"])
        if term["year"] is not None:
            match |= Q(year=term["year"])
        q &= match
    return q


def _count_view(request, product):
    """Count a view once per browser session (a refresh does not add another one)."""
    seen = request.session.get("seen_products", [])
    if product.pk in seen:
        return
    Album_image.objects.filter(pk=product.pk).update(views=F("views") + 1)
    product.views += 1
    request.session["seen_products"] = [*seen, product.pk]


# ------------------------------------------------------------------ pages

@require_safe
def products(request):
    form = ProductFilterForm(request.GET or None)
    terms = parse_terms(form.cleaned_data.get("q")) if form.is_valid() else []

    # is the current user liking each painting? (one query, no loop in Python)
    if request.user.is_authenticated:
        liked = Exists(request.user.liked_paintings.filter(pk=OuterRef("pk")))
    else:
        liked = Value(False, output_field=BooleanField())

    queryset = (
        Album_image.objects
        .filter(_search_q(terms))
        .annotate(like_count=Count("likes"), liked=liked)
        .order_by("-views", "id")          # most viewed first
    )

    chips = []
    if terms:
        remaining = request.GET.copy()
        remaining.pop("q", None)
        chips.append({
            "label": "Search",
            "value": form.cleaned_data["q"],
            "remove": f"?{remaining.urlencode()}",
        })

    return render(request, "shop/products.html", {
        "products": queryset,
        "form": form,
        "chips": chips,
        "searching": bool(terms),
        "result_count": queryset.count(),
        "total_count": Album_image.objects.count(),
    })


@require_safe
def product_details(request, slug):
    product = get_object_or_404(
        Album_image.objects.prefetch_related(
            "images").annotate(like_count=Count("likes")),
        slug=slug,
    )
    _count_view(request, product)
    product.liked = (
        request.user.is_authenticated
        and product.likes.filter(pk=request.user.pk).exists()
    )
    return render(request, "shop/product_details.html", {"product": product})


@require_POST
def toggle_like(request, slug):
    """Called by likes.js: like if not liked yet, unlike if already liked."""
    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "login_required", "login_url": reverse("login")}, status=401
        )

    product = get_object_or_404(Album_image, slug=slug)
    liked = not product.likes.filter(pk=request.user.pk).exists()
    if liked:
        product.likes.add(request.user)
    else:
        product.likes.remove(request.user)
    return JsonResponse({"liked": liked, "count": product.likes.count()})


# -------------------------------------------------------------------- API

class Product_api(APIView):

    def get(self, request):
        data = Album_image.objects.order_by("-views", "id")
        return Response({"data": Album_Serializer(data, many=True).data})

    def post(self, request):
        serializer = Album_Serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Created New Product", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"message": "Could not create the product", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class Product_details_api(APIView):

    def get(self, request, pk):
        product = get_object_or_404(Album_image, pk=pk)
        return Response({"data": Album_Serializer(product).data})

    def put(self, request, pk):
        product = get_object_or_404(Album_image, pk=pk)
        serializer = Album_Serializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Update Accepted", "data": serializer.data},
                status=status.HTTP_202_ACCEPTED,
            )
        return Response(
            {"message": "Update failed", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        get_object_or_404(Album_image, pk=pk).delete()
        return Response({"message": "Deleted"}, status=status.HTTP_204_NO_CONTENT)
