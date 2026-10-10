from django.urls import path
from .views import Product_api, products, Product_details_api, product_details

# Product urls
urlpatterns = [
    path('products/', products, name='products'),
    path('product_details/<slug:slug>/', product_details, name='product_details')
]


# APIs
urlpatterns += [

    path('product/api/', Product_api.as_view(), name='product_api'),
    path('product/api/<int:pk>', Product_details_api.as_view(),
         name='product_api_details'),

]
