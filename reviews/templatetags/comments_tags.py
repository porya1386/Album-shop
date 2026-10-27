from django import template

from ..forms import CommentForm
from ..views import FLASH_KEY

register = template.Library()

PAGE_SIZE = 20


@register.inclusion_tag("reviews/comments.html", takes_context=True)
def comments_section(context, product):
    """{% comments_section product %}  -> the whole comments block."""
    request = context["request"]
    user = request.user

    qs = product.comments.select_related("user")
    total = qs.count()
    show_all = request.GET.get("all_comments") == "1"
    comments = qs if show_all else qs[:PAGE_SIZE]

    # an error from the last POST (and the text the user had typed)
    form_error = ""
    initial = {}
    flash = request.session.get(FLASH_KEY)
    if flash and flash.get("product") == product.slug:
        request.session.pop(FLASH_KEY, None)
        form_error = flash.get("error", "")
        initial = {"body": flash.get("body", "")}

    return {
        "request": request,
        "product": product,
        "comments": comments,
        "total": total,
        "has_more": total > PAGE_SIZE and not show_all,
        "form": CommentForm(initial=initial),
        "form_error": form_error,
        "can_moderate": user.is_authenticated and user.has_perm("reviews.delete_comment"),
    }
