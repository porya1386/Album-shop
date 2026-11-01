from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render, resolve_url
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods, require_POST

from django_ratelimit.decorators import ratelimit

from .forms import LoginForm, RegisterForm
from .password_views import (
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from . import captcha_gate as gate


def _safe_next(request):
    """The ?next= page, but only if it points to THIS site (no open redirect)."""
    target = request.POST.get("next") or request.GET.get("next") or ""
    ok = url_has_allowed_host_and_scheme(
        target, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    )
    return target if ok else ""


def _after_login():
    # settings.LOGIN_REDIRECT_URL is a url NAME ("shop:products"), so the
    # language prefix (/en/ or /fa/) is added automatically.
    return resolve_url(settings.LOGIN_REDIRECT_URL)


# <- put YOUR old numbers here
@ratelimit(key="ip", rate="20/m", method="POST", block=True)
@require_http_methods(["GET", "HEAD", "POST"])
def auth_view(request):
    # unbound: no errors on a fresh page
    login_form = LoginForm(request, show_captcha=gate.needed(request, "login"))
    register_form = RegisterForm(show_captcha=gate.needed(request, "register"))
    mode = "login"
    next_url = _safe_next(request)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "register":
            mode = "register"
            register_form = RegisterForm(
                request.POST, show_captcha=gate.needed(request, "register")
            )
            if register_form.is_valid():
                gate.reset(request, "register")
                user = register_form.save()
                login(request, user)
                messages.success(
                    request,
                    _("Your account was created. Welcome, %(name)s!")
                    % {"name": user.get_username()},
                )
                return redirect(next_url or _after_login())
            # every wrong try counts; forgetting the captcha box does not
            if "captcha" not in register_form.errors:
                gate.add(request, "register")
            if gate.needed(request, "register"):
                register_form.enable_captcha()

        elif action == "login":
            login_form = LoginForm(
                request, data=request.POST, show_captcha=gate.needed(
                    request, "login")
            )
            if login_form.is_valid():
                # success: start again from 0
                gate.reset(request, "login")
                user = login_form.get_user()
                login(request, user)
                messages.success(
                    request,
                    _("Welcome back, %(name)s!") % {
                        "name": user.get_username()},
                )
                if not request.POST.get("remember_me"):
                    # forget when the browser closes
                    request.session.set_expiry(0)
                return redirect(next_url or _after_login())

            if "captcha" not in login_form.errors:
                gate.add(request, "login")
            # this was the 3rd wrong try: the page we send back already has the checkbox
            if gate.needed(request, "login"):
                login_form.enable_captcha()

    return render(request, "accounts/login.html", {
        "login_form": login_form,
        "register_form": register_form,
        "show_captcha": "captcha" in login_form.fields,
        "show_register_captcha": "captcha" in register_form.fields,
        "mode": mode,
        "next": next_url,
    })


@require_POST
def logout_view(request):
    logout(request)
    return redirect(resolve_url(settings.LOGOUT_REDIRECT_URL))


# ---------------------------------------------------------------------------
# Password pages = Django's views + captcha after 3 attempts (password_views.py)
#                  + django-ratelimit (limit per IP).
# The names are the ones used in accounts/urls.py:  views.Limited...View
# Change the rates to the ones you used before.
# ---------------------------------------------------------------------------
@method_decorator(
    ratelimit(key="ip", rate="5/h", method="POST", block=True), name="dispatch")
class LimitedPasswordResetView(PasswordResetView):
    pass


@method_decorator(
    ratelimit(key="ip", rate="10/h", method="POST", block=True), name="dispatch")
class LimitedPasswordResetConfirmView(PasswordResetConfirmView):
    pass


@method_decorator(
    ratelimit(key="user_or_ip", rate="5/h", method="POST", block=True), name="dispatch")
class LimitedPasswordChangeView(PasswordChangeView):
    pass
