from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
    path("add/<str:slug>/", views.add_comment, name="add"),
    path("add-sculpture/<str:slug>/",
         views.add_sculpture_comment, name="add_sculpture"),
    path("delete/<int:pk>/", views.delete_comment, name="delete"),
]
