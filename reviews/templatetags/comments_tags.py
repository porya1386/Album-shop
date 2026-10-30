from django import template

from shop.models import Sculpture

from ..forms import CommentForm
from ..views import FLASH_KEY

register = template.Library()

PAGE_SIZE = 20


@register.inclusion_tag("reviews/comments.html", takes_context=True)
def comments_section(context, target):
    """{% comments_section product %}  or  {% comments_section sculpture %}  -> the comments block."""
    request = context["request"]
    user = request.user

    is_sculpture = isinstance(target, Sculpture)
    flash_id = f"{'sculpture' if is_sculpture else 'product'}:{target.slug}"

    qs = target.comments.select_related("user")
    total = qs.count()
    show_all = request.GET.get("all_comments") == "1"
    comments = qs if show_all else qs[:PAGE_SIZE]

    # an error from the last POST (and the text the user had typed)
    form_error = ""
    initial = {}
    flash = request.session.get(FLASH_KEY)
    if flash and flash.get("target") == flash_id:
        request.session.pop(FLASH_KEY, None)
        form_error = flash.get("error", "")
        initial = {"body": flash.get("body", "")}

    return {
        "request": request,
        "target": target,
        "is_sculpture": is_sculpture,
        "comments": comments,
        "total": total,
        "has_more": total > PAGE_SIZE and not show_all,
        "form": CommentForm(initial=initial),
        "form_error": form_error,
        "can_moderate": user.is_authenticated and user.has_perm("reviews.delete_comment"),
    }
