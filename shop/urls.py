from django.urls import path
from . import views

# Product urls
urlpatterns = [
    path('products/', views.products, name='products'),
    path('product_details/<slug:slug>/',
         views.product_details, name='product_details'),
    path("sculptures/<slug:slug>/",
         views.sculpture_details, name="sculpture_details"),
    path("sculptures/<slug:slug>/like/",
         views.toggle_sculpture_like, name="toggle_sculpture_like"),
    path('products/<slug:slug>/like/', views.toggle_like, name='toggle_like'),
]


# APIs
# urlpatterns += [

#     path('product/api/', Product_api.as_view(), name='product_api'),
#     path('product/api/<int:pk>', Product_details_api.as_view(),
#          name='product_api_details'),

# ]
