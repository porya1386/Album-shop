from django.db.models import Count, Exists, F, OuterRef, Q, Value, BooleanField
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, resolve_url
from django.views.decorators.http import require_POST, require_safe
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .forms import ProductFilterForm
from .models import Album_image, Sculpture
from .search import parse_terms
from .serializer import Album_Serializer
# from rest_framework.permissions import AllowAny, IsAdminUser

# ---------------------------------------------------------------- helpers


def _search_q(terms):
    """Search English and Persian titles/descriptions, price and year."""
    q = Q()

    for term in terms:
        text = term["text"]

        # Search English and Persian content.
        match = (
            Q(title__icontains=text)
            | Q(title_fa__icontains=text)
            | Q(description__icontains=text)
            | Q(description_fa__icontains=text)
        )

        # Search both dollar prices and Toman prices.
        if term["number"] is not None:
            match |= (
                Q(price=term["number"])
                | Q(price_toman=term["number"])
            )

        # Search creation year.
        if term["year"] is not None:
            match |= Q(year__year=term["year"])

        # Apply month if the parser provides one.
        if term.get("month") is not None:
            match &= Q(year__month=term["month"])

        # Every search term must match.
        q &= match

    return q


def _sculpture_search_q(terms):
    """Same idea for sculptures. Their `year` is a plain number (2024), not a date."""
    q = Q()

    for term in terms:
        text = term["text"]

        match = (
            Q(title__icontains=text)
            | Q(title_fa__icontains=text)
            | Q(description__icontains=text)
            | Q(description_fa__icontains=text)
            | Q(material__icontains=text)      # "bronze", "marble", ...
            | Q(size__icontains=text)
        )

        if term["number"] is not None:
            match |= (
                Q(price=term["number"])
                | Q(price_toman=term["number"])
            )

        if term["year"] is not None:
            match |= Q(year=term["year"])

        q &= match

    return q


def _count_view(request, product):
    """Count a view once per browser session."""
    seen = request.session.get("seen_products", [])

    if product.pk in seen:
        return

    Album_image.objects.filter(pk=product.pk).update(
        views=F("views") + 1
    )

    product.views += 1
    request.session["seen_products"] = [*seen, product.pk]


# ------------------------------------------------------------------ pages


COLLECTIONS = ("paintings", "sculptures")


@require_safe
def products(request):
    # ?collection=sculptures -> sculptures; anything else -> paintings (default)
    collection = request.GET.get("collection", "paintings")
    if collection not in COLLECTIONS:
        collection = "paintings"

    form = ProductFilterForm(request.GET or None)

    terms = (
        parse_terms(form.cleaned_data.get("q"))
        if form.is_valid()
        else []
    )

    if collection == "sculptures":
        # Check whether the current user liked each sculpture.
        if request.user.is_authenticated:
            liked = Exists(
                request.user.liked_sculptures.filter(
                    pk=OuterRef("pk")
                )
            )
        else:
            liked = Value(False, output_field=BooleanField())

        queryset = (
            Sculpture.objects
            .filter(_sculpture_search_q(terms))
            .annotate(
                like_count=Count("likes"),
                liked=liked,
            )
            .order_by("-views", "id")
        )
    else:
        # Check whether the current user liked each painting.
        if request.user.is_authenticated:
            liked = Exists(
                request.user.liked_paintings.filter(
                    pk=OuterRef("pk")
                )
            )
        else:
            liked = Value(False, output_field=BooleanField())

        queryset = (
            Album_image.objects
            .filter(_search_q(terms))
            .annotate(
                like_count=Count("likes"),
                liked=liked,
            )
            .order_by("-views", "id")
        )

    paintings_count = Album_image.objects.count()
    sculptures_count = Sculpture.objects.count()

    # Create an individual chip for every search term.
    chips = []

    if terms:
        raw_query = form.cleaned_data.get("q") or ""
        words = raw_query.split()[:len(terms)]

        for index, word in enumerate(words):
            # Keep all existing query parameters.
            remaining = request.GET.copy()

            # Remove only the selected search term.
            remaining_words = (
                words[:index] + words[index + 1:]
            )

            if remaining_words:
                remaining["q"] = " ".join(remaining_words)
            else:
                remaining.pop("q", None)

            query_string = remaining.urlencode()

            # Return to the products page if no parameters remain.
            remove_url = (
                f"?{query_string}"
                if query_string
                else request.path
            )

            # IMPORTANT: This must be inside the for loop.
            chips.append({
                "label": "Search",
                "value": word,
                "remove": remove_url,
            })

    return render(
        request,
        "shop/products.html",
        {
            "collection": collection,
            "products": queryset,
            "form": form,
            "chips": chips,
            "searching": bool(terms),
            "result_count": queryset.count(),
            "total_count": (
                sculptures_count if collection == "sculptures" else paintings_count
            ),
            "paintings_count": paintings_count,
            "sculptures_count": sculptures_count,
        },
    )


@login_required
@require_safe
def product_details(request, slug):
    product = get_object_or_404(
        Album_image.objects
        .prefetch_related("images")
        .annotate(like_count=Count("likes")),
        slug=slug,
    )

    _count_view(request, product)

    product.liked = product.likes.filter(
        pk=request.user.pk
    ).exists()

    return render(
        request,
        "shop/product_details.html",
        {"product": product},
    )


# same rule as product_details; remove this line to make sculptures public
@login_required
@require_safe
def sculpture_details(request, slug):
    sculpture = get_object_or_404(
        Sculpture.objects
        .prefetch_related("images")
        .annotate(like_count=Count("likes")),
        slug=slug,
    )

    # Count a view once per browser session.
    seen = request.session.get("seen_sculptures", [])

    if sculpture.pk not in seen:
        Sculpture.objects.filter(pk=sculpture.pk).update(
            views=F("views") + 1
        )
        sculpture.views += 1
        request.session["seen_sculptures"] = [*seen, sculpture.pk]

    sculpture.liked = sculpture.likes.filter(
        pk=request.user.pk
    ).exists()

    return render(
        request,
        "shop/sculpture_details.html",
        {"sculpture": sculpture},
    )


@require_POST
def toggle_sculpture_like(request, slug):
    """Like a sculpture or remove the existing like."""
    if not request.user.is_authenticated:
        return JsonResponse(
            {
                "error": "login_required",
                "login_url": resolve_url(settings.LOGIN_URL),
            },
            status=401,
        )

    sculpture = get_object_or_404(Sculpture, slug=slug)

    liked = not sculpture.likes.filter(
        pk=request.user.pk
    ).exists()

    if liked:
        sculpture.likes.add(request.user)
    else:
        sculpture.likes.remove(request.user)

    return JsonResponse({
        "liked": liked,
        "count": sculpture.likes.count(),
    })


@require_POST
def toggle_like(request, slug):
    """Like a painting or remove the existing like."""
    if not request.user.is_authenticated:
        return JsonResponse(
            {
                "error": "login_required",
                "login_url": resolve_url(settings.LOGIN_URL),
            },
            status=401,
        )

    product = get_object_or_404(Album_image, slug=slug)

    liked = not product.likes.filter(
        pk=request.user.pk
    ).exists()

    if liked:
        product.likes.add(request.user)
    else:
        product.likes.remove(request.user)

    return JsonResponse({
        "liked": liked,
        "count": product.likes.count(),
    })


# -------------------------------------------------------------------- API


# class Product_api(APIView):

#     def get(self, request):
#         data = Album_image.objects.order_by("-views", "id")

#         return Response({
#             "data": Album_Serializer(data, many=True).data
#         })

#     def post(self, request):
#         serializer = Album_Serializer(data=request.data)

#         if serializer.is_valid():
#             serializer.save()

#             return Response(
#                 {
#                     "message": "Created New Product",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_201_CREATED,
#             )

#         return Response(
#             {
#                 "message": "Could not create the product",
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )


# class Product_details_api(APIView):

#     def get(self, request, pk):
#         product = get_object_or_404(Album_image, pk=pk)

#         return Response({
#             "data": Album_Serializer(product).data
#         })

#     def put(self, request, pk):
#         product = get_object_or_404(Album_image, pk=pk)

#         serializer = Album_Serializer(
#             product,
#             data=request.data,
#             partial=True,
#         )

#         if serializer.is_valid():
#             serializer.save()

#             return Response(
#                 {
#                     "message": "Update Accepted",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_202_ACCEPTED,
#             )

#         return Response(
#             {
#                 "message": "Update failed",
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )

#     def delete(self, request, pk):
#         product = get_object_or_404(Album_image, pk=pk)
#         product.delete()

#         return Response(
#             {"message": "Deleted"},
#             status=status.HTTP_204_NO_CONTENT,
#         )
