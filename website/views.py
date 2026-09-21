from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect


# Create your views here.


def home(request):
    return render(request, 'website/home.html', {})


def products(request):
    return render(request, 'website/products.html', {})


def login(request):
    return render(request, 'website/login.html', {})


def about(reqeust):
    return render(reqeust, 'website/about.html', {})


def register(request):
    form = None
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration complete. Welcome!")
            return redirect("home")
    return render(request, "login.html", {"register_form": form})
