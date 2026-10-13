from django.urls import path
from .views import *

# Product urls
urlpatterns = [
    path('products/', products, name='products'),
    path('product_details/<slug:slug>/',
         product_details, name='product_details'),
    path('products/<slug:slug>/like/', toggle_like, name='toggle_like'),
]


# APIs
urlpatterns += [

    path('product/api/', Product_api.as_view(), name='product_api'),
    path('product/api/<int:pk>', Product_details_api.as_view(),
         name='product_api_details'),

]
