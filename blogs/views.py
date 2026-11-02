from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import PostForm
from .models import Post


def can_write(user):
    return user.is_authenticated and user.has_perm("blogs.add_post")


class PostListView(ListView):
    model = Post
    template_name = "blogs/post_list.html"
    context_object_name = "posts"
    paginate_by = 9

    def get_queryset(self):
        qs = Post.objects.select_related("author")
        # writers also see drafts (marked in the template); everybody else only live posts
        if can_write(self.request.user) and self.request.GET.get("all"):
            return qs
        return qs.published()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["can_write"] = can_write(self.request.user)
        ctx["show_all"] = bool(self.request.GET.get("all"))
        return ctx


class PostDetailView(DetailView):
    model = Post
    template_name = "blogs/post_detail.html"
    context_object_name = "post"

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        user = self.request.user
        if not post.is_live and not user.has_perm("blogs.change_post"):
            raise Http404                      # drafts are private
        return post

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["can_edit"] = self.request.user.has_perm("blogs.change_post")
        ctx["can_delete"] = self.request.user.has_perm("blogs.delete_post")
        return ctx


class PostCreateView(PermissionRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blogs/post_form.html"
    permission_required = "blogs.add_post"        # not logged in / no permission -> 403 / login

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, _("The post was saved."))
        return super().form_valid(form)


class PostUpdateView(PermissionRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blogs/post_form.html"
    permission_required = "blogs.change_post"

    def form_valid(self, form):
        messages.success(self.request, _("The post was saved."))
        return super().form_valid(form)


class PostDeleteView(PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = "blogs/post_confirm_delete.html"
    permission_required = "blogs.delete_post"
    success_url = reverse_lazy("blogs:list")

    def form_valid(self, form):
        messages.success(self.request, _("The post was deleted."))
        return super().form_valid(form)
