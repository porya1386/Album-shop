"""Password pages with the captcha shown only after 3 attempts.

Save as:  accounts/password_views.py
They are the normal Django views + the captcha rule. Keep the other arguments you
already pass in urls.py (template_name, success_url, email_template_name ...).
"""
from django.contrib.auth import views as auth_views

from .captcha_gate import CaptchaGateMixin
from .forms import (
    CaptchaPasswordChangeForm,
    CaptchaPasswordResetForm,
    CaptchaSetPasswordForm,
)


class PasswordResetView(CaptchaGateMixin, auth_views.PasswordResetView):
    form_class = CaptchaPasswordResetForm
    captcha_key = "password_reset"
    count_success = True          # a reset mail request always "works": every send counts


class PasswordResetConfirmView(CaptchaGateMixin, auth_views.PasswordResetConfirmView):
    form_class = CaptchaSetPasswordForm
    captcha_key = "password_set"


class PasswordChangeView(CaptchaGateMixin, auth_views.PasswordChangeView):
    form_class = CaptchaPasswordChangeForm
    captcha_key = "password_change"
