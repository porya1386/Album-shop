
from django.urls import path
from . import views
from accounts.forms import LoginForm
urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
]

