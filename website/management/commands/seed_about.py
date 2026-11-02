"""Fill the About page with the text that is on the site now, so the owner edits instead of writing from zero.

    python manage.py seed_about

Does nothing if the About page already exists (it never overwrites the owner's text).
"""
from django.core.management.base import BaseCommand

from website.models import AboutFact, AboutPage

EN = """
<h2>A web developer who likes slow mornings, tidy code and projects that leave people a little calmer than they found them.</h2>
<p>My name is Your Name, and I build websites and web applications for a living. Most of my work is done with Python and Django, with HTML, CSS and a little JavaScript on the front. I enjoy the whole path of a project: talking through the idea, shaping the data, writing the code, and watching the first real person use it.</p>
<p>I work best with small teams and individual clients who know what they want to achieve but are not sure how to get there. Explaining technical things in plain words is a part of the job I take seriously.</p>
<blockquote>A good website should feel like a quiet room: everything is where you expect it to be.</blockquote>
<h2>How I got here</h2>
<p>I started programming because I wanted to build a small tool for myself and could not find one that did exactly what I needed. That first tool was rough, but it worked, and I was hooked. Since then I have studied, taken on freelance projects, worked with companies and learned a lot from mistakes along the way.</p>
<h2>How I work</h2>
<p>I like to start small. Before writing much code I make a rough plan, agree on what the first useful version looks like, and build that. After that we improve it step by step.</p>
<h2>Away from the screen</h2>
<p>When I am not working I like long walks, landscape paintings, cooking for friends and reading books I probably should have finished last year.</p>
<h2>Let's talk</h2>
<p>If you have a project, a question or just want to say hello, I would be happy to hear from you. I usually reply within a couple of days.</p>
"""

FA = """
<h2>توسعه‌دهنده‌ی وبی که صبح‌های آرام، کد مرتب و پروژه‌هایی را دوست دارد که مردم را کمی آرام‌تر از آنچه بودند رها کنند.</h2>
<p>نام من «نام شما» است و کارم ساختن وب‌سایت و برنامه‌های وب است. بیشتر کارم با پایتون و جنگو انجام می‌شود و در بخش نمایش از HTML و CSS و کمی جاوااسکریپت استفاده می‌کنم. از کل مسیر یک پروژه لذت می‌برم: گفتگو درباره‌ی ایده، شکل دادن به داده‌ها، نوشتن کد و دیدن اولین کاربر واقعی که از آن استفاده می‌کند.</p>
<p>با تیم‌های کوچک و کارفرمایان تکی بهتر کار می‌کنم؛ کسانی که می‌دانند چه می‌خواهند ولی مطمئن نیستند چطور به آن برسند. توضیح دادن موضوعات فنی با زبان ساده بخشی از کار است که جدی می‌گیرم.</p>
<blockquote>یک وب‌سایت خوب باید مثل یک اتاق آرام باشد: همه‌چیز همان‌جا که انتظار دارید قرار دارد.</blockquote>
<h2>چطور به اینجا رسیدم</h2>
<p>برنامه‌نویسی را شروع کردم چون می‌خواستم ابزار کوچکی برای خودم بسازم و ابزاری پیدا نکردم که دقیقاً همان کار را بکند. آن ابزار اول ناپخته بود، اما کار می‌کرد و من شیفته شدم. از آن زمان درس خوانده‌ام، پروژه‌های فریلنس گرفته‌ام، با شرکت‌ها کار کرده‌ام و در این مسیر از اشتباهاتم چیزهای زیادی یاد گرفته‌ام.</p>
<h2>چطور کار می‌کنم</h2>
<p>دوست دارم از کوچک شروع کنم. پیش از نوشتن کد زیاد یک طرح کلی می‌کشم، درباره‌ی نخستین نسخه‌ی مفید توافق می‌کنیم و همان را می‌سازم. بعد قدم‌به‌قدم بهترش می‌کنیم.</p>
<h2>دور از صفحه‌ی نمایش</h2>
<p>وقتی کار نمی‌کنم پیاده‌روی‌های طولانی، نقاشی‌های منظره، آشپزی برای دوستان و خواندن کتاب‌هایی را دوست دارم که احتمالاً باید پارسال تمامشان می‌کردم.</p>
<h2>بیایید حرف بزنیم</h2>
<p>اگر پروژه‌ای، پرسشی دارید یا فقط می‌خواهید سلام کنید، خوشحال می‌شوم خبری از شما بشنوم. معمولاً ظرف چند روز پاسخ می‌دهم.</p>
"""

FACTS = [
    ("Based in", "Your City, Your Country", "محل زندگی", "شهر شما، کشور شما"),
    ("Works with", "Python, Django, HTML, CSS, JavaScript, PostgreSQL",
     "ابزارهای کاری", "Python, Django, HTML, CSS, JavaScript, PostgreSQL"),
    ("Languages", "Persian, English", "زبان‌ها", "فارسی، انگلیسی"),
    ("Availability", "Open to new projects",
     "آمادگی برای کار", "پذیرای پروژه‌های جدید"),
]


class Command(BaseCommand):
    help = "Create the About page with the current text (only if it does not exist yet)."

    def handle(self, *args, **opts):
        if AboutPage.objects.exists():
            self.stdout.write(
                "The About page already exists: nothing changed.")
            return
        page = AboutPage.objects.create(
            title="About me", title_fa="درباره من",
            lead="A web developer who likes slow mornings, tidy code and projects that leave people a little calmer than they found them.",
            lead_fa="توسعه‌دهنده‌ی وبی که صبح‌های آرام، کد مرتب و پروژه‌هایی را دوست دارد که مردم را کمی آرام‌تر از آنچه بودند رها کنند.",
            body=EN.strip(), body_fa=FA.strip(), email="you@example.com",
        )
        for i, (label, value, label_fa, value_fa) in enumerate(FACTS, start=1):
            AboutFact.objects.create(about=page, order=i, label=label, value=value,
                                     label_fa=label_fa, value_fa=value_fa)
        self.stdout.write(self.style.SUCCESS(
            "About page created. Edit it in the admin: About page."))
