"""One-time conversion of OLD plain-text posts to the HTML the editor uses.

    python manage.py convert_posts_to_html            (shows what would change)
    python manage.py convert_posts_to_html --apply    (does it)

Posts that are already HTML are not touched, so it is safe to run twice.
"""
import re

from django.core.management.base import BaseCommand
from django.utils.html import escape

from blogs.models import Post

HTML_RE = re.compile(
    r"<\s*(p|h[1-6]|ul|ol|figure|div|table|blockquote|pre)\b", re.IGNORECASE)
TOKEN = re.compile(r"^\[\s*image\s+(\d+)\s*\]$", re.IGNORECASE)


def to_html(text, images):
    out = []
    for block in re.split(r"\n\s*\n", text.replace("\r\n", "\n")):
        block = block.strip()
        if not block:
            continue
        lines, buf = block.split("\n"), []
        for line in lines + [None]:
            m = TOKEN.match(line.strip()) if line is not None else None
            if line is None or m:
                if buf:
                    out.append("<p>%s</p>" % "<br>".join(escape(x)
                               for x in buf))
                    buf = []
                if m and int(m.group(1)) in images:
                    img = images[int(m.group(1))]
                    cap = img.caption or ""
                    out.append('<figure class="image"><img src="%s" alt="%s">%s</figure>' % (
                        img.image.url, escape(cap),
                        "<figcaption>%s</figcaption>" % escape(cap) if cap else ""))
            else:
                buf.append(line)
    return "".join(out)


class Command(BaseCommand):
    help = "Convert old plain-text blog posts to HTML for the editor."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true")

    def handle(self, *args, **opts):
        changed = 0
        for post in Post.objects.prefetch_related("images"):
            images = {i.order: i for i in post.images.all()}
            dirty = []
            for field in ("body", "body_fa"):
                value = getattr(post, field) or ""
                if value.strip() and not HTML_RE.search(value):
                    setattr(post, field, to_html(value, images))
                    dirty.append(field)
            if dirty:
                changed += 1
                self.stdout.write("%s: %s" % (post.title, ", ".join(dirty)))
                if opts["apply"]:
                    post.save(update_fields=dirty)
        self.stdout.write(self.style.SUCCESS(
            "%d post(s) %s." % (changed, "converted" if opts["apply"] else "would be converted (add --apply)")))
