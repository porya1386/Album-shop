from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "id": "reg-email",
            "autocomplete": "email",
            "placeholder": "Enter your email",
        }),
    )

    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "id": "reg-username",
            "autocomplete": "username",
            "placeholder": "Choose a username",
        }),
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "id": "reg-password1",
            "autocomplete": "new-password",
            "minlength": "8",
        }),
    )

    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={
            "id": "reg-password2",
            "autocomplete": "new-password",
            "minlength": "8",
        }),
    )

    captcha = ReCaptchaField(
        label="",
        error_messages={
            "required": "Please confirm that you are not a robot."},
        widget=ReCaptchaV2Checkbox(attrs={
            "id": "register-captcha",
            "data-theme": "dark",
            "data-callback": "onCaptchaSolved_register",
            "data-expired-callback": "onCaptchaExpired_register",
        }),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """Django's login form + Google reCAPTCHA v2 ("I'm not a robot")."""

    captcha = ReCaptchaField(
        label="",
        error_messages={
            "required": "Please confirm that you are not a robot."},
        widget=ReCaptchaV2Checkbox(attrs={
            "id": "login-captcha",
            "data-theme": "dark",
            # login_captcha.js enables the button
            "data-callback": "onCaptchaSolved_login",
            "data-expired-callback": "onCaptchaExpired_login",
        }),
    )

    def clean(self):
        # No captcha (or a wrong one) -> do not even check the password,
        # so a bot cannot guess passwords without solving the captcha.
        if "captcha" in self.errors:
            return self.cleaned_data
        return super().clean()
