from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('login/', views.login, name='login'),
    path('products/', views.products, name='products')
]


urlpatterns += [
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("register/", views.register, name="register"),
]
