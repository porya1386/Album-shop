from django.shortcuts import render
from rest_framework.decorators import api_view, APIView
from rest_framework.response import Response
from .models import Album_image
from .serializer import Album_Serializer
from rest_framework import status
from django.shortcuts import get_object_or_404


def products(request):
    # ORM
    data = Album_image.objects.all().order_by('id')
    return render(request, 'shop/products.html', {'products': data})


def product_details(request, slug):
    data = get_object_or_404(
        Album_image.objects.prefetch_related('images'), slug=slug)
    return render(request, 'shop/product_details.html', {'product': data})


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
        data = Album_image.objects.get(id=pk)
        serializer = Album_Serializer(data, many=False)
        return Response({"data": serializer.data}, status=status.HTTP_202_ACCEPTED)

    def put(self, request, pk):
        data = Album_image.objects.get(id=pk)
        serializer = Album_Serializer(data, data=request.data, partial=True)
        return Response({"message": "Update Accepted", "data": serializer.data}, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        data = Album_image.objects.get(id=pk)
        data.delete()
        return Response({"message": "Deleted"}, status=status.HTTP_204_NO_CONTENT)
