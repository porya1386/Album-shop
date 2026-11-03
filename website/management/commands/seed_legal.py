"""Save as  website/management/commands/seed_legal.py
Creates the 4 legal pages with a ready TEMPLATE text (English + Persian). Run once:
    python manage.py seed_legal
Existing pages are NOT overwritten (use --force to overwrite).
Then open Admin -> Legal pages and replace [YOUR NAME], [ADDRESS] etc. This is a general template, NOT legal advice:
have it checked by a lawyer before you start selling.
"""
from django.core.management.base import BaseCommand

from website.models import AboutPage, LegalPage

SITE = "Jahan"

EN = {
    "terms": ("Terms of Service", """
<h2>1. About these terms</h2>
<p>These terms apply to your use of the website {SITE} (the “Site”), operated by [YOUR NAME] (“we”, “us”). By using the Site you agree to them. If you do not agree, please do not use the Site.</p>
<h2>2. Accounts</h2>
<p>You can create an account with an email address or with Google or GitHub. You must give correct information, keep your password secret and tell us if you think someone else has used your account. You are responsible for what happens under your account. We may suspend accounts that break these terms or are used for abuse.</p>
<h2>3. Artworks and how to buy</h2>
<p>The Site is a gallery and shop window for original paintings and sculptures. There is no online checkout: to buy a work you contact us (by the email on the Site), and we agree on availability, price, payment and delivery together in writing. A work is reserved for you only when we confirm it to you. Every original work is unique. Colours on a screen can look slightly different from the real work; sizes and materials are described as exactly as possible.</p>
<h2>4. Prices</h2>
<p>Prices on the Site are for information. We may change them or withdraw a work at any time. The price that counts is the one we confirm to you in writing.</p>
<h2>5. Payment and delivery</h2>
<p>Payment and delivery are arranged directly between you and us after we confirm a purchase. We will tell you the conditions (payment method, packing, shipping cost, delivery time and what happens if a work arrives damaged) before you pay.</p>
<h2>6. Copyright</h2>
<p>All artworks, photographs, texts and designs on the Site belong to [YOUR NAME] or are used with permission. Buying a work gives you the physical object, not the copyright. You may not copy, sell or publish the images or texts without written permission. Private sharing with a link back to the Site is welcome.</p>
<h2>7. Your content</h2>
<p>If you write comments, you keep ownership of them but allow us to show them on the Site. Do not post anything unlawful, hateful, misleading or that belongs to someone else. We may remove comments and accounts that do.</p>
<h2>8. Acceptable use</h2>
<p>Do not try to break, overload or gain unauthorised access to the Site, use bots to collect its content, or use it for fraud.</p>
<h2>9. Liability</h2>
<p>We work to keep the Site correct and available but provide it “as is”. As far as the law allows, we are not liable for indirect losses or for interruptions outside our control. Nothing in these terms limits rights that you have by law as a consumer.</p>
<h2>10. Changes and law</h2>
<p>We may update these terms; the date at the top shows the latest version. These terms follow the laws of [YOUR COUNTRY].</p>
<h2>11. Contact</h2>
<p>Questions: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
"""),
    "privacy": ("Privacy Policy", """
<h2>1. Who we are</h2>
<p>{SITE} is operated by [YOUR NAME], [ADDRESS]. You can reach us at <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
<h2>2. What we collect</h2>
<ul>
<li><b>Account data:</b> name or username, email address and an encrypted password. If you sign in with Google or GitHub we receive your name, email address and profile picture from them. We never see your Google or GitHub password.</li>
<li><b>Messages:</b> what you write to us (email, name, phone if you give it) when you ask about a work.</li>
<li><b>Content you write:</b> comments, likes and reviews.</li>
<li><b>Technical data:</b> IP address, browser type and security logs, to protect the Site.</li>
</ul>
<h2>3. Why we use it</h2>
<p>To run your account, answer your messages and arrange purchases you ask for, keep the Site secure and prevent spam, and to improve the Site. We do not sell your data and we do not use it for advertising.</p>
<h2>4. reCAPTCHA</h2>
<p>Some forms (login, registration, password reset) are protected by Google reCAPTCHA. It checks that you are a person and may collect technical information such as your IP address and browser data. Google's own privacy policy and terms apply to that service.</p>
<h2>5. Who receives your data</h2>
<p>Only the services we need: our hosting provider, our email service, the delivery company (only if you buy a work: address and phone), Google (sign-in, reCAPTCHA) and GitHub (sign-in). We do not share it with anyone else unless the law requires it.</p>
<h2>6. How long we keep it</h2>
<p>Account data until you delete your account. Purchase records as long as accounting or tax law requires. Security logs for a short period.</p>
<h2>7. Your rights</h2>
<p>You can ask to see, correct, export or delete your data, and to close your account, by writing to <a href="mailto:{EMAIL}">{EMAIL}</a>. We will answer within a reasonable time.</p>
<h2>8. Cookies</h2>
<p>See our <a href="/legal/cookies/">Cookie Policy</a>.</p>
<h2>9. Security and children</h2>
<p>Passwords are stored encrypted and the Site is served over HTTPS. The Site is not meant for children under 16.</p>
<h2>10. Changes</h2>
<p>If we change this policy, the date above is updated.</p>
"""),
    "cookies": ("Cookie Policy", """
<h2>What are cookies?</h2>
<p>Cookies are small files a website stores in your browser. We use only what is needed for the Site to work and a tiny local setting for your comfort. We use <b>no advertising or tracking cookies</b>.</p>
<h2>What we use</h2>
<ul>
<li><b>Session cookie</b> (sessionid): keeps you logged in and counts a post view once per visit. Removed when the session ends or you log out.</li>
<li><b>Security cookie</b> (csrftoken): protects forms against forgery.</li>
<li><b>Language cookie:</b> remembers English or Persian.</li>
<li><b>Local storage – theme and notice:</b> remembers the theme you chose and that you closed the cookie notice. It stays in your browser only.</li>
<li><b>Google reCAPTCHA:</b> on login and registration forms, Google may set its own cookies to detect bots.</li>
<li><b>Google / GitHub sign-in:</b> only if you choose to sign in with them.</li>
</ul>
<h2>Your choice</h2>
<p>You can delete or block cookies in your browser settings. The Site will still open, but login, language and forms may stop working.</p>
<h2>Questions</h2>
<p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
"""),
}

FA = {
    "terms": ("شرایط استفاده از خدمات", """
<h2>۱. درباره این شرایط</h2>
<p>این شرایط برای استفاده شما از وب‌سایت {SITE} («سایت») که توسط [نام شما] اداره می‌شود، اعمال می‌شود. با استفاده از سایت، این شرایط را می‌پذیرید. اگر موافق نیستید لطفاً از سایت استفاده نکنید.</p>
<h2>۲. حساب کاربری</h2>
<p>می‌توانید با ایمیل یا با گوگل و گیت‌هاب حساب بسازید. اطلاعات واردشده باید درست باشد، رمز عبور را محرمانه نگه دارید و اگر فکر می‌کنید کسی از حساب شما استفاده کرده به ما اطلاع دهید. مسئولیت آنچه با حساب شما انجام می‌شود با شماست. حساب‌هایی که این شرایط را نقض کنند یا سوءاستفاده شوند ممکن است مسدود شوند.</p>
<h2>۳. آثار و نحوه خرید</h2>
<p>سایت یک گالری و ویترین برای نقاشی‌ها و مجسمه‌های اصیل است. خرید آنلاین (سبد خرید) وجود ندارد: برای خرید یک اثر با ما (از طریق ایمیل درج‌شده در سایت) تماس می‌گیرید و درباره موجودی، قیمت، پرداخت و تحویل کتبی توافق می‌کنیم. اثر فقط پس از تأیید ما برای شما رزرو می‌شود. هر اثر اصلی یگانه است. رنگ‌ها روی صفحه نمایش ممکن است اندکی با اثر واقعی تفاوت داشته باشند؛ اندازه و جنس تا حد امکان دقیق ذکر می‌شود.</p>
<h2>۴. قیمت</h2>
<p>قیمت‌های سایت جنبه اطلاع‌رسانی دارند. ممکن است هر زمان تغییر کنند یا اثری کنار گذاشته شود. قیمتی معتبر است که کتبی به شما تأیید می‌کنیم.</p>
<h2>۵. پرداخت و تحویل</h2>
<p>پرداخت و تحویل پس از تأیید خرید، مستقیماً بین شما و ما ترتیب داده می‌شود. شرایط (روش پرداخت، بسته‌بندی، هزینه ارسال، زمان تحویل و اقدام در صورت آسیب‌دیدن اثر) را پیش از پرداخت به شما اعلام می‌کنیم.</p>
<h2>۶. حقوق مالکیت</h2>
<p>همه آثار، عکس‌ها، متن‌ها و طراحی‌های سایت متعلق به [نام شما] است یا با اجازه استفاده شده است. خرید اثر، مالکیت جسم اثر را به شما می‌دهد، نه حق تکثیر آن را. کپی، فروش یا انتشار تصاویر و متن‌ها بدون اجازه کتبی مجاز نیست. اشتراک‌گذاری شخصی همراه با پیوند به سایت آزاد است.</p>
<h2>۷. محتوای شما</h2>
<p>اگر نظر بنویسید مالکیت آن با شماست اما به ما اجازه نمایش در سایت را می‌دهید. محتوای غیرقانونی، توهین‌آمیز، گمراه‌کننده یا متعلق به دیگران منتشر نکنید. ما می‌توانیم چنین نظرها و حساب‌هایی را حذف کنیم.</p>
<h2>۸. استفاده مجاز</h2>
<p>تلاش برای مختل‌کردن سایت، فشار بیش از حد، دسترسی غیرمجاز، جمع‌آوری خودکار محتوا با ربات یا استفاده برای کلاهبرداری ممنوع است.</p>
<h2>۹. مسئولیت</h2>
<p>ما تلاش می‌کنیم سایت درست و در دسترس باشد، اما آن را «به همان شکل موجود» ارائه می‌کنیم. تا حدی که قانون اجازه می‌دهد، مسئول خسارت‌های غیرمستقیم یا وقفه‌های خارج از کنترل خود نیستیم. هیچ بخشی از این شرایط حقوق قانونی شما به‌عنوان مصرف‌کننده را محدود نمی‌کند.</p>
<h2>۱۰. تغییرات و قانون حاکم</h2>
<p>این شرایط ممکن است به‌روزرسانی شود؛ تاریخ بالای صفحه آخرین نسخه را نشان می‌دهد. این شرایط تابع قوانین [کشور شما] است.</p>
<h2>۱۱. ارتباط با ما</h2>
<p>پرسش‌ها: <a href="mailto:{EMAIL}">{EMAIL}</a></p>
"""),
    "privacy": ("سیاست حفظ حریم خصوصی", """
<h2>۱. ما که هستیم</h2>
<p>{SITE} توسط [نام شما]، [نشانی] اداره می‌شود. ایمیل: <a href="mailto:{EMAIL}">{EMAIL}</a></p>
<h2>۲. چه اطلاعاتی جمع می‌کنیم</h2>
<ul>
<li><b>اطلاعات حساب:</b> نام یا نام کاربری، ایمیل و رمز عبور رمزنگاری‌شده. اگر با گوگل یا گیت‌هاب وارد شوید نام، ایمیل و عکس پروفایل شما را از آن‌ها دریافت می‌کنیم. رمز گوگل یا گیت‌هاب شما را هرگز نمی‌بینیم.</li>
<li><b>پیام‌ها:</b> آنچه هنگام پرسش درباره یک اثر برای ما می‌نویسید (ایمیل، نام، و تلفن اگر بدهید).</li>
<li><b>محتوایی که می‌نویسید:</b> نظرها، لایک‌ها و دیدگاه‌ها.</li>
<li><b>اطلاعات فنی:</b> نشانی IP، نوع مرورگر و گزارش‌های امنیتی برای محافظت از سایت.</li>
</ul>
<h2>۳. برای چه استفاده می‌کنیم</h2>
<p>برای مدیریت حساب، پاسخ به پیام‌ها و ترتیب‌دادن خریدی که درخواست می‌کنید، امنیت و جلوگیری از هرزنامه و بهبود سایت. اطلاعات شما را نمی‌فروشیم و برای تبلیغات استفاده نمی‌کنیم.</p>
<h2>۴. reCAPTCHA</h2>
<p>برخی فرم‌ها (ورود، ثبت‌نام، بازیابی رمز) با Google reCAPTCHA محافظت می‌شوند. این سرویس بررسی می‌کند که شما انسان هستید و ممکن است اطلاعات فنی مانند IP و مرورگر را جمع کند. سیاست و شرایط خود گوگل برای آن سرویس اعمال می‌شود.</p>
<h2>۵. اطلاعات با چه کسانی به اشتراک گذاشته می‌شود</h2>
<p>فقط سرویس‌های لازم: شرکت میزبانی، سرویس ایمیل، شرکت حمل‌ونقل (فقط اگر اثری بخرید: نشانی و تلفن)، گوگل و گیت‌هاب (ورود و reCAPTCHA). جز در صورت الزام قانونی با دیگران به اشتراک نمی‌گذاریم.</p>
<h2>۶. مدت نگهداری</h2>
<p>اطلاعات حساب تا زمان حذف حساب. سوابق خرید تا زمانی که قانون مالیاتی و حسابداری لازم می‌داند. گزارش‌های امنیتی برای مدت کوتاه.</p>
<h2>۷. حقوق شما</h2>
<p>می‌توانید درخواست مشاهده، اصلاح، دریافت یا حذف اطلاعات و بستن حساب را با ایمیل <a href="mailto:{EMAIL}">{EMAIL}</a> بدهید. در زمان معقول پاسخ می‌دهیم.</p>
<h2>۸. کوکی‌ها</h2>
<p><a href="/legal/cookies/">سیاست کوکی</a> را ببینید.</p>
<h2>۹. امنیت و کودکان</h2>
<p>رمزها رمزنگاری‌شده ذخیره می‌شوند و سایت با HTTPS ارائه می‌شود. سایت برای کودکان زیر ۱۶ سال نیست.</p>
<h2>۱۰. تغییرات</h2>
<p>اگر این سیاست تغییر کند، تاریخ بالا به‌روز می‌شود.</p>
"""),
    "cookies": ("سیاست کوکی", """
<h2>کوکی چیست؟</h2>
<p>کوکی‌ها فایل‌های کوچکی هستند که سایت در مرورگر شما ذخیره می‌کند. ما فقط موارد لازم برای کار سایت و یک تنظیم محلی کوچک برای راحتی شما را به‌کار می‌بریم. <b>از کوکی تبلیغاتی یا ردیابی استفاده نمی‌کنیم.</b></p>
<h2>چه چیزهایی استفاده می‌شود</h2>
<ul>
<li><b>کوکی نشست</b> (sessionid): شما را وارد نگه می‌دارد و بازدید هر نوشته را یک‌بار می‌شمارد. با پایان نشست یا خروج پاک می‌شود.</li>
<li><b>کوکی امنیتی</b> (csrftoken): از فرم‌ها در برابر جعل محافظت می‌کند.</li>
<li><b>کوکی زبان:</b> فارسی یا انگلیسی بودن را به یاد می‌سپارد.</li>
<li><b>حافظه محلی – تم و اعلان:</b> تمی که انتخاب کرده‌اید و بسته‌شدن اعلان کوکی را به یاد می‌سپارد و فقط در مرورگر شما می‌ماند.</li>
<li><b>Google reCAPTCHA:</b> در فرم‌های ورود و ثبت‌نام، گوگل ممکن است کوکی خودش را برای تشخیص ربات بگذارد.</li>
<li><b>ورود با گوگل / گیت‌هاب:</b> فقط اگر خودتان این روش را انتخاب کنید.</li>
</ul>
<h2>انتخاب شما</h2>
<p>می‌توانید کوکی‌ها را در تنظیمات مرورگر حذف یا مسدود کنید؛ سایت باز می‌شود اما ورود، زبان و فرم‌ها ممکن است کار نکنند.</p>
<h2>پرسش‌ها</h2>
<p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
"""),
}


class Command(BaseCommand):
    help = "Create the legal pages (terms, privacy, cookies) with a template text."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true",
                            help="overwrite pages that already exist")

    def handle(self, *args, **opts):
        about = AboutPage.objects.first()
        email = (about.email if about and about.email else "your-email@example.com")
        for slug, (title, body) in EN.items():
            fa_title, fa_body = FA[slug]

            def fill(t): return t.replace(
                "{SITE}", SITE).replace("{EMAIL}", email).strip()
            obj, created = LegalPage.objects.get_or_create(slug=slug, defaults={
                "title": title, "title_fa": fa_title, "body": fill(body), "body_fa": fill(fa_body)})
            if not created and opts["force"]:
                obj.title, obj.title_fa, obj.body, obj.body_fa = title, fa_title, fill(
                    body), fill(fa_body)
                obj.save()
            self.stdout.write(("created: " if created else (
                "overwritten: " if opts["force"] else "kept: ")) + slug)
        self.stdout.write(self.style.WARNING(
            "Now replace [YOUR NAME], [ADDRESS], [YOUR COUNTRY] and the [numbers] in Admin -> Legal pages."))
