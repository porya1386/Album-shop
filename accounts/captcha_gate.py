"""Show the reCAPTCHA only after a few attempts in the same browser session.

Save as:  accounts/captcha_gate.py

Every form has its own counter (login, register, password_reset, password_change,
password_set), stored in request.session. Default: the captcha appears from the 4th
try, i.e. after 3 attempts. Change it in settings.py:   CAPTCHA_AFTER_ATTEMPTS = 3
"""
from django.conf import settings

SESSION_KEY = "captcha_attempts"


def limit():
    return getattr(settings, "CAPTCHA_AFTER_ATTEMPTS",
                   getattr(settings, "LOGIN_CAPTCHA_AFTER", 3))


def attempts(request, key):
    return request.session.get(SESSION_KEY, {}).get(key, 0)


def needed(request, key):
    return attempts(request, key) >= limit()


def add(request, key):
    data = dict(request.session.get(SESSION_KEY, {}))
    data[key] = data.get(key, 0) + 1
    request.session[SESSION_KEY] = data        # assign again so Django saves the session


def reset(request, key):
    data = dict(request.session.get(SESSION_KEY, {}))
    if data.pop(key, None) is not None:
        request.session[SESSION_KEY] = data


class CaptchaGateMixin:
    """Put it FIRST in the base classes of the Django password views.

    captcha_key    name of the counter ("password_reset", ...)
    count_success  True for forms that always 'work' (password reset request): every
                   send counts as an attempt. False: only wrong tries count, and a
                   success sets the counter back to 0.
    """
    captcha_key = None
    count_success = False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["show_captcha"] = needed(self.request, self.captcha_key)
        return kwargs

    def form_invalid(self, form):
        # forgetting to tick the box is not a "wrong try"
        if "captcha" not in form.errors:
            add(self.request, self.captcha_key)
        if needed(self.request, self.captcha_key):
            form.enable_captcha()
        return super().form_invalid(form)

    def form_valid(self, form):
        if self.count_success:
            add(self.request, self.captcha_key)
        else:
            reset(self.request, self.captcha_key)
        return super().form_valid(form)
