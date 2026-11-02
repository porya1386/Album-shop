"""Blog pages. Posts are added / edited / deleted ONLY in the admin panel (/admin/blogs/post/)."""
import json
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Exists, F, OuterRef
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, resolve_url
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from .models import Post, PostComment

VIEWED_KEY = "blog_viewed"
COMMENT_LIMIT = 5                      # per user per minute
COMMENT_WINDOW = timedelta(minutes=1)
PAGE_SIZE_COMMENTS = 20


class PostListView(ListView):
    template_name = "blogs/post_list.html"
    context_object_name = "posts"
    paginate_by = 9

    def get_queryset(self):
        qs = (Post.objects.published()
              .select_related("author")
              .annotate(like_total=Count("likes", distinct=True),
                        comment_total=Count("comments", distinct=True)))
        user = self.request.user
        if user.is_authenticated:
            qs = qs.annotate(liked=Exists(
                Post.objects.filter(pk=OuterRef("pk"), likes=user)))
        return qs


class PostDetailView(DetailView):
    template_name = "blogs/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        qs = Post.objects.select_related("author").prefetch_related("images")
        # people who may edit posts in the admin can preview a draft; everybody else sees only live posts
        if self.request.user.has_perm("blogs.change_post"):
            return qs
        return qs.published()

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self._count_view(request)
        return response

    def _count_view(self, request):
        """One view per visitor per post per browser session (a refresh does not count again)."""
        post = self.object
        if not post.is_live:
            return
        seen = request.session.get(VIEWED_KEY, [])
        if post.pk not in seen:
            Post.objects.filter(pk=post.pk).update(views=F("views") + 1)
            post.views += 1
            request.session[VIEWED_KEY] = (seen + [post.pk])[-200:]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        post, user = self.object, self.request.user

        comments = post.comments.select_related("user")
        total = comments.count()
        show_all = self.request.GET.get("all_comments") == "1"

        ctx.update({
            "like_total": post.likes.count(),
            "liked": user.is_authenticated and post.likes.filter(pk=user.pk).exists(),
            "comments": comments if show_all else comments[:PAGE_SIZE_COMMENTS],
            "comment_total": total,
            "has_more": total > PAGE_SIZE_COMMENTS and not show_all,
            "can_moderate": user.has_perm("blogs.delete_postcomment"),
            "comment_error": self.request.session.pop("blog_comment_error", ""),
            "comment_draft": self.request.session.pop("blog_comment_draft", ""),
        })
        return ctx


@require_POST
def toggle_like(request, slug):
    """Like / unlike a post. Answers JSON: {"liked": true, "count": 3}."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login_required", "login_url": resolve_url(settings.LOGIN_URL)}, status=401)

    post = get_object_or_404(Post.objects.published(), slug=slug)
    liked = not post.likes.filter(pk=request.user.pk).exists()
    if liked:
        post.likes.add(request.user)
    else:
        post.likes.remove(request.user)
    return JsonResponse({"liked": liked, "count": post.likes.count()})


@login_required
@require_POST
def add_comment(request, slug):
    post = get_object_or_404(Post.objects.published(), slug=slug)
    body = (request.POST.get("body") or "").strip()
    error = ""

    if len(body) < 3:
        error = _("Your comment is too short.")
    elif len(body) > 1000:
        error = _("Your comment is too long.")
    else:
        since = timezone.now() - COMMENT_WINDOW
        if PostComment.objects.filter(user=request.user, created_at__gte=since).count() >= COMMENT_LIMIT:
            error = _("You are commenting too fast. Please wait a minute.")

    if error:
        request.session["blog_comment_error"] = str(error)
        request.session["blog_comment_draft"] = body[:1000]
        return redirect(post.get_absolute_url() + "#comments")

    comment = PostComment.objects.create(
        post=post, user=request.user, body=body)
    return redirect(f"{post.get_absolute_url()}#comment-{comment.pk}")


@login_required
@require_POST
def delete_comment(request, pk):
    comment = get_object_or_404(
        PostComment.objects.select_related("post"), pk=pk)
    allowed = comment.user_id == request.user.id or request.user.has_perm(
        "blogs.delete_postcomment")
    if not allowed:
        raise Http404
    post = comment.post
    comment.delete()
    messages.success(request, _("The comment was deleted."))
    return redirect(post.get_absolute_url() + "#comments")
