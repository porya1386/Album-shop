import re

from django import template
from django.template.defaultfilters import linebreaksbr
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe

from ..models import Post

register = template.Library()

HTML_RE = re.compile(
    r"<\s*(p|h[1-6]|ul|ol|figure|div|table|blockquote|pre)\b", re.IGNORECASE)
LINE_TOKEN = re.compile(r"^\[\s*(image|video)\s+(\d+)\s*\]$", re.IGNORECASE)
# the editor wraps a line of text in <p>: "<p>[video 1]</p>"  (spaces and &nbsp; are allowed)
P_TOKEN = re.compile(
    r"<p[^>]*>(?:\s|&nbsp;|<br\s*/?>)*\[\s*(image|video)\s+(\d+)\s*\](?:\s|&nbsp;|<br\s*/?>)*</p>",
    re.IGNORECASE,
)


@register.simple_tag
def latest_posts(limit=8):
    """{% latest_posts as posts %}  -> the newest published posts (for the home page)."""
    return list(Post.objects.published().order_by("-published_at", "-id")[:limit])


def _image_html(post, img):
    text = img.display_caption
    caption = format_html("<figcaption>{}</figcaption>", text) if text else ""
    return format_html('<figure class="blog-figure"><img src="{}" alt="{}" loading="lazy">{}</figure>',
                       img.image.url, text or post.display_title, caption)


def _video_html(post, vid):
    text = vid.display_caption
    caption = format_html("<figcaption>{}</figcaption>", text) if text else ""
    poster = format_html(' poster="{}"', vid.poster.url) if vid.poster else ""
    return format_html(
        '<figure class="blog-figure blog-video"><video controls playsinline preload="metadata" src="{}"{}></video>{}</figure>',
        vid.video.url, poster, caption)


@register.filter
def blog_body(post):
    """{{ post|blog_body }}  -> the text of the post.

    * text written with the editor is HTML: shown as it is (only admins / moderators can write it)
    * a line  [video 1]  or  [image 1]  becomes the video / picture added under "Videos in the text"
    * videos / pictures that are not placed in the text are shown after it
    * old plain-text posts are escaped and turned into paragraphs
    """
    raw = post.display_body or ""
    images = {i.order: i for i in post.images.all()}
    videos = {v.order: v for v in post.videos.all()}
    used = set()

    def media(kind, number):
        if kind == "video" and number in videos:
            used.add(("video", number))
            return _video_html(post, videos[number])
        if kind == "image" and number in images:
            used.add(("image", number))
            return _image_html(post, images[number])
        return ""                                    # unknown number: nothing

    if HTML_RE.search(raw):
        html = P_TOKEN.sub(lambda m: media(
            m.group(1).lower(), int(m.group(2))), raw)
        out = [mark_safe(html)]
    else:
        out = []
        for block in re.split(r"\n\s*\n", raw.replace("\r\n", "\n")):
            block = block.strip()
            if not block:
                continue
            buf = []
            for line in block.split("\n") + [None]:
                m = LINE_TOKEN.match(
                    line.strip()) if line is not None else None
                if line is None or m:
                    if buf:
                        out.append(format_html(
                            "<p>{}</p>", mark_safe(linebreaksbr(conditional_escape("\n".join(buf))))))
                        buf = []
                    if m:
                        out.append(media(m.group(1).lower(), int(m.group(2))))
                else:
                    buf.append(line)

    for number, vid in videos.items():
        if ("video", number) not in used:
            out.append(_video_html(post, vid))
    for number, img in images.items():
        if ("image", number) not in used:
            out.append(_image_html(post, img))
    return mark_safe("".join(str(x) for x in out))
