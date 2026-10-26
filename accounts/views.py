from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import RegisterForm
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST

from .forms import LoginForm, RegisterForm

AFTER_LOGIN = "/shop/products"


def _safe_next(request):
    """The ?next= page, but only if it points to THIS site (no open redirect)."""
    target = request.POST.get("next") or request.GET.get("next") or ""
    ok = url_has_allowed_host_and_scheme(
        target, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    )
    return target if ok else ""


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
                return redirect(next_url or AFTER_LOGIN)

        elif action == "login":
            login_form = LoginForm(request, data=request.POST)
            if login_form.is_valid():
                login(request, login_form.get_user())
                if not request.POST.get("remember_me"):
                    # forget when the browser closes
                    request.session.set_expiry(0)
                return redirect(next_url or AFTER_LOGIN)

    return render(request, "accounts/login.html", {
        "login_form": login_form,
        "register_form": register_form,
        "mode": mode,
        "next": next_url,
    })


@require_POST
def logout_view(request):
    logout(request)
    return redirect("/")


def register(request):
    form = None
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration complete. Welcome!")
            return redirect("home")
    return render(request, "login.html", {"register_form": form})
