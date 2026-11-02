"""For people who signed in with Google/GitHub and never chose a password.
Save as: accounts/password_set_view.py   (or paste into accounts/views.py)"""
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _


@login_required
def password_set_view(request):
    # already has a password -> normal "change password" page (asks the old one)
    if request.user.has_usable_password():
        return redirect("accounts:password_change")

    form = SetPasswordForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        update_session_auth_hash(request, request.user)   # stay logged in
        messages.success(request, _(
            "Your password is set. You can now also sign in with it."))
        return redirect("accounts:password_change")
    return render(request, "accounts/password_set_form.html", {"form": form})
