import re

from django import template
from django.template.defaultfilters import linebreaksbr
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe

from ..models import Post

register = template.Library()


@register.simple_tag
def latest_posts(limit=8):
    """{% latest_posts as posts %}  -> the newest published posts (for the home page)."""
    return list(Post.objects.published().order_by("-published_at", "-id")[:limit])


_TOKEN = re.compile(r"^\[\s*image\s+(\d+)\s*\]$", re.IGNORECASE)


@register.filter
def blog_body(post):
    """{{ post|blog_body }}  -> the text as paragraphs, with  [image 2]  lines replaced by the picture.

    Everything the author typed is escaped (no HTML can be injected). Pictures that are not
    placed in the text are shown after it."""
    raw = post.display_body or ""
    # text written with the editor is HTML: show it as it is (only admins / moderators can write it)
    if re.search(r"<\s*(p|h[1-6]|ul|ol|figure|div|table|blockquote|pre)\b", raw, re.IGNORECASE):
        return mark_safe(raw)

    # old posts (plain text): paragraphs + [image N] lines
    images = {img.order: img for img in post.images.all()}
    used = set()
    out = []

    def figure(img):
        text = img.display_caption
        caption = format_html(
            "<figcaption>{}</figcaption>", text) if text else ""
        return format_html('<figure class="blog-figure"><img src="{}" alt="{}" loading="lazy">{}</figure>',
                           img.image.url, text or post.display_title, caption)

    for block in re.split(r"\n\s*\n", raw.replace("\r\n", "\n")):
        block = block.strip()
        if not block:
            continue
        # a block may be: text, a token, or text lines with a token on a line of its own
        parts, buf = [], []
        for line in block.split("\n"):
            m = _TOKEN.match(line.strip())
            if m:
                if buf:
                    parts.append(("text", "\n".join(buf)))
                    buf = []
                parts.append(("img", int(m.group(1))))
            else:
                buf.append(line)
        if buf:
            parts.append(("text", "\n".join(buf)))

        for kind, value in parts:
            if kind == "text":
                out.append(format_html(
                    "<p>{}</p>", mark_safe(linebreaksbr(conditional_escape(value)))))
            elif value in images:
                used.add(value)
                out.append(figure(images[value]))
            # an unknown number is simply ignored

    for number, img in images.items():
        if number not in used:
            out.append(figure(img))
    return mark_safe("".join(out))
