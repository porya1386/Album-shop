from django.urls import path
from .views import home

urlpatterns = [
    path('product/',home,name='products')
]
