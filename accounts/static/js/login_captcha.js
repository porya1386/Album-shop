/* reCAPTCHA on the login AND register forms: each submit button stays disabled
   until that form's captcha is ticked. The server checks the captcha again, so
   this only makes the page clearer.
   Form markup:  <form data-captcha-form="login"> ... [data-captcha-hint] ... [data-captcha-submit]
   Google calls  onCaptchaSolved_<name> / onCaptchaExpired_<name>  (data-callback in forms.py). */
(function () {
    "use strict";

    var forms = document.querySelectorAll("form[data-captcha-form]");

    Array.prototype.forEach.call(forms, function (form) {
        var name = form.getAttribute("data-captcha-form");
        var button = form.querySelector("[data-captcha-submit]");
        var hint = form.querySelector("[data-captcha-hint]");
        if (!name || !button) return;

        function allow(ok) {
            button.disabled = !ok;
            button.setAttribute("aria-disabled", ok ? "false" : "true");
            if (hint) hint.hidden = ok;
        }

        window["onCaptchaSolved_" + name] = function () { allow(true); };
        window["onCaptchaExpired_" + name] = function () { allow(false); };
        form._captchaAllow = allow;
        allow(false);
    });

    // Back button: the old ticks are gone, so ask again
    window.addEventListener("pageshow", function (e) {
        if (!e.persisted) return;
        if (window.grecaptcha && typeof window.grecaptcha.reset === "function") {
            try { window.grecaptcha.reset(); } catch (err) { /* ignore */ }
        }
        Array.prototype.forEach.call(forms, function (form) {
            if (form._captchaAllow) form._captchaAllow(false);
        });
    });
})();