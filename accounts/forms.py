from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox

from .models import CustomUser

CAPTCHA_REQUIRED = _("Please confirm that you are not a robot.")


def _captcha(**attrs):
    """One place for the reCAPTCHA field, so every form behaves the same."""
    attrs.setdefault("data-theme", "dark")
    return ReCaptchaField(
        label="",
        error_messages={"required": CAPTCHA_REQUIRED},
        widget=ReCaptchaV2Checkbox(attrs=attrs),
    )


class OptionalCaptchaMixin:
    """The form has NO captcha at first. Views call enable_captcha() (or pass
    show_captcha=True) after a few attempts, see captcha_gate.py."""

    captcha_attrs = {}

    def __init__(self, *args, show_captcha=False, **kwargs):
        super().__init__(*args, **kwargs)
        if show_captcha:
            self.enable_captcha()

    def enable_captcha(self):
        """Add the checkbox. Safe after is_valid(): errors already found stay the same."""
        if "captcha" in self.fields:
            return
        field = _captcha(**self.captcha_attrs)
        # box in the page language
        field.widget.api_params = {"hl": get_language() or "en"}
        self.fields["captcha"] = field


class RegisterForm(OptionalCaptchaMixin, UserCreationForm):
    email = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=forms.EmailInput(attrs={
            "id": "reg-email",
            "autocomplete": "email",
            "placeholder": _("Enter your email"),
        }),
    )

    username = forms.CharField(
        label=_("Username"),
        required=True,
        widget=forms.TextInput(attrs={
            "id": "reg-username",
            "autocomplete": "username",
            "placeholder": _("Choose a username"),
        }),
    )

    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            "id": "reg-password1",
            "autocomplete": "new-password",
            "minlength": "8",
        }),
    )

    password2 = forms.CharField(
        label=_("Confirm password"),
        widget=forms.PasswordInput(attrs={
            "id": "reg-password2",
            "autocomplete": "new-password",
            "minlength": "8",
        }),
    )

    captcha_attrs = {
        "id": "register-captcha",
        "data-callback": "onCaptchaSolved_register",
        "data-expired-callback": "onCaptchaExpired_register",
    }

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("This email is already registered."))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class LoginForm(OptionalCaptchaMixin, AuthenticationForm):
    """Django's login form. The reCAPTCHA is added after 3 wrong tries (captcha_gate.py)."""

    captcha_attrs = {
        "id": "login-captcha",
        # login_captcha.js enables the button
        "data-callback": "onCaptchaSolved_login",
        "data-expired-callback": "onCaptchaExpired_login",
    }

    def clean(self):
        # Captcha is shown but missing/wrong -> do not even check the password,
        # so a bot cannot guess passwords without solving the captcha.
        if "captcha" in self.errors:
            return self.cleaned_data
        return super().clean()


class CaptchaPasswordResetForm(OptionalCaptchaMixin, PasswordResetForm):
    captcha_attrs = {"id": "password-reset-captcha"}


class CaptchaSetPasswordForm(OptionalCaptchaMixin, SetPasswordForm):
    captcha_attrs = {"id": "set-password-captcha"}


class CaptchaPasswordChangeForm(OptionalCaptchaMixin, PasswordChangeForm):
    captcha_attrs = {"id": "password-change-captcha"}
