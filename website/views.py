from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from shop.models import Album_image

# Create your views here.


def home(request):
    products = Album_image.objects.order_by('-create_at')[:12]
    return render(request, 'website/home.html', {'products': products})


def about(reqeust):
    return render(reqeust, 'website/about.html', {})
