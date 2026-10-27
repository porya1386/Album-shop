from django.conf import settings
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render, resolve_url
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST

from .forms import LoginForm, RegisterForm


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


@require_http_methods(["GET", "HEAD", "POST"])
def auth_view(request):
    # unbound: no errors on a fresh page
    login_form = LoginForm(request)
    register_form = RegisterForm()
    mode = "login"
    next_url = _safe_next(request)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "register":
            mode = "register"
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                login(request, register_form.save())
                return redirect(next_url or _after_login())

        elif action == "login":
            login_form = LoginForm(request, data=request.POST)
            if login_form.is_valid():
                login(request, login_form.get_user())
                if not request.POST.get("remember_me"):
                    # forget when the browser closes
                    request.session.set_expiry(0)
                return redirect(next_url or _after_login())

    return render(request, "accounts/login.html", {
        "login_form": login_form,
        "register_form": register_form,
        "mode": mode,
        "next": next_url,
    })


@require_POST
def logout_view(request):
    logout(request)
    return redirect(resolve_url(settings.LOGOUT_REDIRECT_URL))
