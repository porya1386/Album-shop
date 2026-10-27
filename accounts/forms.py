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


class CaptchaLanguageMixin:
    """Show the reCAPTCHA box in the language of the current page."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field = self.fields.get("captcha")
        if field is not None:
            field.widget.api_params = {"hl": get_language() or "en"}


class RegisterForm(CaptchaLanguageMixin, UserCreationForm):
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

    captcha = _captcha(**{
        "id": "register-captcha",
        "data-callback": "onCaptchaSolved_register",
        "data-expired-callback": "onCaptchaExpired_register",
    })

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


class LoginForm(CaptchaLanguageMixin, AuthenticationForm):
    """Django's login form + Google reCAPTCHA v2 ("I'm not a robot")."""

    captcha = _captcha(**{
        "id": "login-captcha",
        # login_captcha.js enables the button
        "data-callback": "onCaptchaSolved_login",
        "data-expired-callback": "onCaptchaExpired_login",
    })

    def clean(self):
        # No captcha (or a wrong one) -> do not even check the password,
        # so a bot cannot guess passwords without solving the captcha.
        if "captcha" in self.errors:
            return self.cleaned_data
        return super().clean()


class CaptchaPasswordResetForm(CaptchaLanguageMixin, PasswordResetForm):
    captcha = _captcha(id="password-reset-captcha")


class CaptchaSetPasswordForm(CaptchaLanguageMixin, SetPasswordForm):
    captcha = _captcha(id="set-password-captcha")


class CaptchaPasswordChangeForm(CaptchaLanguageMixin, PasswordChangeForm):
    captcha = _captcha(id="password-change-captcha")
