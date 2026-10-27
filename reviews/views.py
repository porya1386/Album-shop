from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from shop.models import Album_image

from .forms import CommentForm
from .models import Comment

# at most 5 comments per user per minute
RATE_LIMIT = 5
RATE_WINDOW = timedelta(minutes=1)
FLASH_KEY = "comment_flash"


def _product_url(product):
    return reverse("product_details", args=[product.slug]) + "#comments"


def can_delete(user, comment):
    """The author, or anybody with the 'delete comment' permission (superuser, moderators)."""
    if not user.is_authenticated:
        return False
    return comment.user_id == user.id or user.has_perm("reviews.delete_comment")


@login_required
@require_POST
def add_comment(request, slug):
    product = get_object_or_404(Album_image, slug=slug)
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
            comment.product = product
            comment.user = request.user
            comment.save()
            return redirect(_product_url(product).replace("#comments", f"#comment-{comment.pk}"))
    else:
        error = " ".join(str(e) for e in form.errors.get(
            "body", [])) or _("Invalid comment.")

    # Show the error (and keep the typed text) on the product page
    request.session[FLASH_KEY] = {
        "product": product.slug,
        "body": request.POST.get("body", "")[:1000],
        "error": str(error),
    }
    return redirect(_product_url(product))


@login_required
@require_POST
def delete_comment(request, pk):
    comment = get_object_or_404(
        Comment.objects.select_related("product"), pk=pk)
    if not can_delete(request.user, comment):
        # 404, not 403: do not reveal that the comment exists
        return redirect(_product_url(comment.product))
    product = comment.product
    comment.delete()
    return redirect(_product_url(product))
