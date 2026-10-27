from django import template
from django.urls import translate_url

register = template.Library()


@register.simple_tag(takes_context=True)
def switch_lang_url(context, lang_code):
    """URL of the CURRENT page in another language, e.g. /fa/products/ -> /products/.

    No cookie and no POST: the language is decided only by the URL, so it
    cannot "stick" on the old language.
    """
    request = context["request"]
    return translate_url(request.get_full_path(), lang_code)
