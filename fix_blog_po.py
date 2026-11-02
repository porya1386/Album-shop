"""Repairs the blog part of locale/fa/LC_MESSAGES/django.po.

Usage (Windows cmd, project root, .venv active):
    python fix_blog_po.py locale\\fa\\LC_MESSAGES\\django.po
    python manage.py compilemessages
then STOP the server and start it again.

What it does (a backup django.po.bak is made first):
  * sets the correct Persian text for every blog / home message (fills the empty ones,
    replaces the wrong "guessed" ones that makemessages copied from other texts)
  * removes the "#, fuzzy" flag and the "#| msgid" lines from those messages
    (Django IGNORES fuzzy messages - that is why the blog stayed English)
  * deletes the messages of the old "write a post" pages (they no longer exist)
  * removes duplicate messages (keeps the first one)
"""
import re
import shutil
import sys

TRANSLATIONS = {
    "Blog": "وبلاگ",
    "Blog | Jahan": "وبلاگ | جهان",
    "News, stories and notes from the studio.": "خبرها، داستان‌ها و یادداشت‌هایی از استودیو.",
    "Statistics": "آمار",
    "Comment": "نظر",
    "Read more": "ادامه مطلب",
    "No posts yet.": "هنوز مطلبی نیست.",
    "Newer": "جدیدتر",
    "Older": "قدیمی‌تر",
    "Pages": "صفحه‌ها",
    "Back to blog": "بازگشت به وبلاگ",
    "Like this post": "پسندیدن این مطلب",
    "Write a comment...": "نظر خود را بنویسید...",
    "to leave a comment.": "تا بتوانید نظر بگذارید.",
    "Delete": "حذف",
    "The comment was deleted.": "نظر حذف شد.",
    "Show all %(comment_total)s comments": "نمایش همه‌ی %(comment_total)s نظر",
    "Your comment is too short.": "نظر شما خیلی کوتاه است.",
    "Your comment is too long.": "نظر شما خیلی بلند است.",
    "Draft": "پیش‌نویس",
    "Published": "منتشرشده",
    "Post": "مطلب",
    "Posts": "مطالب",
    "Title": "عنوان",
    "Leave empty: it is made from the title.": "خالی بگذارید: از عنوان ساخته می‌شود.",
    "Cover image": "تصویر شاخص",
    "Short summary": "خلاصه کوتاه",
    "Text": "متن",
    "Author": "نویسنده",
    "Status": "وضعیت",
    "Published at": "زمان انتشار",
    "The image must be smaller than %(mb)s MB.": "حجم تصویر باید کمتر از %(mb)s مگابایت باشد.",
    "Persian short summary": "خلاصه کوتاه فارسی",
    "Persian text": "متن فارسی",
    "Text shown on the Persian site. Leave empty to use the English text.":
        "متنی که در سایت فارسی نمایش داده می‌شود. اگر خالی باشد متن انگلیسی نمایش داده می‌شود.",
    "Persian caption": "زیرنویس فارسی",
    "Latest works": "تازه‌ترین آثار",
    "Paintings and sculptures. Hover to pause, click a work to read more about it.":
        "نقاشی‌ها و مجسمه‌ها. برای توقف ماوس را روی تصویر نگه دارید و برای خواندن درباره هر اثر روی آن کلیک کنید.",
    "See all products": "دیدن همه محصولات",
    "From the blog": "از وبلاگ",
    "Read the blog": "خواندن وبلاگ",
    "Image": "تصویر",
    "Number": "شماره",
    "Write [image NUMBER] on its own line in the text where the picture should appear.":
        "در متن، در یک خط جداگانه [image شماره] بنویسید تا تصویر همان‌جا نمایش داده شود.",
    "Image in text": "تصویر داخل متن",
    "Images in text": "تصاویر داخل متن",
    # video messages that were empty / wrong
    "Video": "ویدیو",
    "Play video": "پخش ویدیو",
    "Upload an image OR a video (MP4 or WebM, up to 100 MB).":
        "یک تصویر یا یک ویدیو (MP4 یا WebM، تا ۱۰۰ مگابایت) بارگذاری کنید.",
    "Upload either an image or a video (not both, not empty).":
        "یا یک تصویر بارگذاری کنید یا یک ویدیو (نه هر دو، نه هیچ‌کدام).",
    "The video is too big. The maximum size is %(mb)s MB.":
        "ویدیو خیلی بزرگ است. حداکثر حجم %(mb)s مگابایت است.",
}

# messages of the old pages for writing posts on the site (deleted)
REMOVE = {
    "Post title", "One or two sentences for the list page", "Delete post | Jahan", "Delete this post?",
    "Yes, delete", "Edit", "Edit post", "New post", "Save", "Write a post", "Only published",
    "Show drafts too", "The post was saved.", "The post was deleted.",
}


def unquote(line):
    m = re.search(r'"(.*)"\s*$', line)
    return m.group(1).replace('\\"', '"').replace("\\n", "\n").replace("\\\\", "\\") if m else ""


def quote(text):
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def parse(lines):
    entries, cur = [], None

    def new():
        return {"comments": [], "ctx": [], "id": [], "plural": False, "str": [], "raw": [], "state": "c", "obsolete": False}

    for line in lines:
        s = line.rstrip("\n")
        if not s.strip():
            continue
        if cur is None:
            cur = new()
        starts = s.startswith("msgctxt ") or s.startswith("msgid ") or (s.startswith("#") and not s.startswith("#~"))
        if cur["state"] == "s" and starts:
            entries.append(cur)
            cur = new()
        if s.startswith("#~"):
            cur["obsolete"] = True
            cur["raw"].append(line)
            cur["state"] = "s"
            continue
        if s.startswith("#"):
            cur["comments"].append(line)
            continue
        if s.startswith("msgctxt "):
            cur["state"] = "x"; cur["ctx"].append(unquote(s)); cur["raw"].append(line)
        elif s.startswith("msgid_plural "):
            cur["state"] = "p"; cur["plural"] = True; cur["raw"].append(line)
        elif s.startswith("msgid "):
            cur["state"] = "i"; cur["id"].append(unquote(s)); cur["raw"].append(line)
        elif s.startswith("msgstr"):
            cur["state"] = "s"; cur["str"].append(unquote(s)); cur["raw"].append(line)
        elif s.startswith('"'):
            cur["raw"].append(line)
            if cur["state"] == "x": cur["ctx"].append(unquote(s))
            elif cur["state"] == "i": cur["id"].append(unquote(s))
            elif cur["state"] == "s": cur["str"].append(unquote(s))
    if cur:
        entries.append(cur)
    return entries


def main(path):
    shutil.copyfile(path, path + ".bak")
    with open(path, encoding="utf-8", newline="") as f:
        lines = f.read().replace("\r\n", "\n").splitlines(True)

    out, seen = [], set()
    done = set()
    log = {"fixed": 0, "removed": 0, "dupes": 0}

    for e in parse(lines):
        if e["obsolete"]:
            out.append("".join(e["comments"] + e["raw"]).rstrip("\n") + "\n")
            continue
        msgid = "".join(e["id"])
        key = ("".join(e["ctx"]), msgid)
        if msgid in REMOVE and not e["ctx"]:
            log["removed"] += 1
            continue
        if key in seen and msgid:
            log["dupes"] += 1
            continue
        seen.add(key)

        if msgid in TRANSLATIONS and not e["plural"] and not e["ctx"]:
            comments = [c for c in e["comments"]
                        if not c.startswith("#|") and not re.match(r"#,.*fuzzy", c)]
            # keep other flags (python-format ...)
            comments = [re.sub(r",\s*fuzzy", "", c) if c.startswith("#,") else c for c in comments]
            body = "msgid %s\nmsgstr %s\n" % (quote(msgid), quote(TRANSLATIONS[msgid]))
            out.append("".join(comments) + body)
            done.add(msgid)
            log["fixed"] += 1
        else:
            out.append("".join(e["comments"] + e["raw"]).rstrip("\n") + "\n")

    # messages that are not in the file yet
    for msgid, text in TRANSLATIONS.items():
        if msgid not in done:
            out.append("msgid %s\nmsgstr %s\n" % (quote(msgid), quote(text)))
            log["fixed"] += 1

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out))
    print("fixed/added: %(fixed)d   removed old pages: %(removed)d   duplicates removed: %(dupes)d" % log)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
