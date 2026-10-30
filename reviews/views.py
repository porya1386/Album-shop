from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from shop.models import Album_image, Sculpture

from .forms import CommentForm
from .models import Comment

# at most 5 comments per user per minute
RATE_LIMIT = 5
RATE_WINDOW = timedelta(minutes=1)
FLASH_KEY = "comment_flash"


def _target_url(target):
    name = "sculpture_details" if isinstance(
        target, Sculpture) else "product_details"
    return reverse(name, args=[target.slug]) + "#comments"


def _is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


def can_delete(user, comment):
    """The author, or anybody with the 'delete comment' permission (superuser, moderators)."""
    if not user.is_authenticated:
        return False
    return comment.user_id == user.id or user.has_perm("reviews.delete_comment")


def _post_comment(request, target, field):
    """Shared by paintings (field='product') and sculptures (field='sculpture')."""
    form = CommentForm(request.POST)
    error = None

    if form.is_valid():
        since = timezone.now() - RATE_WINDOW
        recent = Comment.objects.filter(
            user=request.user, created_at__gte=since).count()
        if recent >= RATE_LIMIT:
            error = _("You are commenting too fast. Please wait a minute.")
        else:
            comment = form.save(commit=False)
            setattr(comment, field, target)
            comment.user = request.user
            comment.save()
            if _is_ajax(request):
                # the page adds this one comment by itself: no reload
                html = render_to_string(
                    "reviews/_comment.html",
                    {
                        "c": comment,
                        "can_moderate": request.user.has_perm("reviews.delete_comment"),
                    },
                    request=request,
                )
                return JsonResponse({
                    "ok": True,
                    "html": html,
                    "count": target.comments.count(),
                })
            return redirect(_target_url(target).replace("#comments", f"#comment-{comment.pk}"))
    else:
        error = " ".join(str(e) for e in form.errors.get(
            "body", [])) or _("Invalid comment.")

    if _is_ajax(request):
        return JsonResponse({"ok": False, "error": str(error)}, status=400)

    # Show the error (and keep the typed text) on the details page
    request.session[FLASH_KEY] = {
        "target": f"{field}:{target.slug}",
        "body": request.POST.get("body", "")[:1000],
        "error": str(error),
    }
    return redirect(_target_url(target))


@login_required
@require_POST
def add_comment(request, slug):
    product = get_object_or_404(Album_image, slug=slug)
    return _post_comment(request, product, "product")


@login_required
@require_POST
def add_sculpture_comment(request, slug):
    sculpture = get_object_or_404(Sculpture, slug=slug)
    return _post_comment(request, sculpture, "sculpture")


@login_required
@require_POST
def delete_comment(request, pk):
    comment = get_object_or_404(
        Comment.objects.select_related("product", "sculpture"), pk=pk)
    target = comment.target
    if not can_delete(request.user, comment):
        if _is_ajax(request):
            return JsonResponse({"ok": False}, status=403)
        return redirect(_target_url(target))
    comment.delete()
    if _is_ajax(request):
        return JsonResponse({"ok": True, "count": target.comments.count()})
    return redirect(_target_url(target))
