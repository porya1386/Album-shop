from django.urls import path

from . import views

app_name = "blogs"

urlpatterns = [
    path("", views.PostListView.as_view(), name="list"),
    path("new/", views.PostCreateView.as_view(), name="create"),
    path("<str:slug>/edit/", views.PostUpdateView.as_view(), name="edit"),
    path("<str:slug>/delete/", views.PostDeleteView.as_view(), name="delete"),
    path("<str:slug>/", views.PostDetailView.as_view(), name="detail"),
]
