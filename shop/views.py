from django.db.models import Count, F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Album_image
from .serializer import Album_Serializer


def products(request):
    # ORM: every painting + how many likes it has
    data = list(
        Album_image.objects.annotate(like_count=Count('likes')).order_by('id')
    )

    # which of them did the logged-in user like?
    liked_ids = set()
    if request.user.is_authenticated:
        liked_ids = set(
            request.user.liked_paintings.values_list('id', flat=True))
    for item in data:
        item.liked = item.id in liked_ids

    return render(request, 'shop/products.html', {'products': data})


def product_details(request, slug):
    data = get_object_or_404(
        Album_image.objects.prefetch_related(
            'images').annotate(like_count=Count('likes')),
        slug=slug,
    )

    # count a view once per browser session (a refresh does not add another one)
    seen = request.session.get('seen_products', [])
    if data.pk not in seen:
        Album_image.objects.filter(pk=data.pk).update(views=F('views') + 1)
        data.views += 1
        seen.append(data.pk)
        request.session['seen_products'] = seen

    data.liked = (
        request.user.is_authenticated
        and data.likes.filter(pk=request.user.pk).exists()
    )
    return render(request, 'shop/product_details.html', {'product': data})


@require_POST
def toggle_like(request, slug):
    # called by likes.js: like if not liked yet, unlike if already liked
    if not request.user.is_authenticated:
        return JsonResponse(
            {'error': 'login_required', 'login_url': reverse('login')}, status=401
        )

    product = get_object_or_404(Album_image, slug=slug)
    if product.likes.filter(pk=request.user.pk).exists():
        product.likes.remove(request.user)
        liked = False
    else:
        product.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': product.likes.count()})


# APIS


class Product_api(APIView):

    def get(self, request):
        data = Album_image.objects.all().order_by('id')
        serializer = Album_Serializer(data, many=True)
        return Response({"data": serializer.data})

    def post(self, request):
        serializer = Album_Serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Created New Product", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"message": "Didnt Add or create something went wrong", "erors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class Product_details_api(APIView):
    def get(self, request, pk):
        data = get_object_or_404(Album_image, id=pk)
        serializer = Album_Serializer(data, many=False)
        return Response({"data": serializer.data}, status=status.HTTP_202_ACCEPTED)

    def put(self, request, pk):
        data = get_object_or_404(Album_image, id=pk)
        serializer = Album_Serializer(data, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Update Accepted", "data": serializer.data}, status=status.HTTP_202_ACCEPTED)
        return Response({"message": "Update failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        data = get_object_or_404(Album_image, id=pk)
        data.delete()
        return Response({"message": "Deleted"}, status=status.HTTP_204_NO_CONTENT)
