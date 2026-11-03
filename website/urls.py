
from django.urls import path
from . import views
from accounts.forms import LoginForm
from . import legal_views
urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path("legal/<slug:slug>/", legal_views.legal_page, name="legal"),
]
