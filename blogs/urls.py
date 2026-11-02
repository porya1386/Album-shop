from django.urls import path

from . import views

app_name = "blogs"

urlpatterns = [
    path("", views.PostListView.as_view(), name="list"),
    path("comment/<int:pk>/delete/", views.delete_comment, name="comment_delete"),
    path("<str:slug>/like/", views.toggle_like, name="like"),
    path("<str:slug>/comment/", views.add_comment, name="comment"),
    path("<str:slug>/", views.PostDetailView.as_view(), name="detail"),
]
