/* reCAPTCHA on the login and register forms.
   Save as:  static/js/login_captcha.js   (replaces the old file)

   The captcha checkbox is shown only after 3 attempts (server side), so this script:
   - form WITHOUT a captcha box  -> the submit button works normally, nothing is blocked;
   - form WITH a captcha box     -> the button stays disabled until the box is ticked.
   The server checks the captcha again, so this only makes the page clearer.

   Optional markup:  <form data-captcha-form="login"> ... [data-captcha-hint] ... [data-captcha-submit]
   Google calls  onCaptchaSolved_<name> / onCaptchaExpired_<name>  (data-callback in forms.py). */
(function () {
    "use strict";

    var forms = document.querySelectorAll("form[data-captcha-form]");

    function hasCaptcha(form) {
        return !!form.querySelector(".g-recaptcha, [data-sitekey], textarea[name='g-recaptcha-response']");
    }

    Array.prototype.forEach.call(forms, function (form) {
        var name = form.getAttribute("data-captcha-form");
        var button = form.querySelector("[data-captcha-submit]") ||
                     form.querySelector("button[type='submit']:not([form])");
        var hint = form.querySelector("[data-captcha-hint]");
        if (!name || !button) return;

        function allow(ok) {
            button.disabled = !ok;
            button.setAttribute("aria-disabled", ok ? "false" : "true");
            if (hint) hint.hidden = ok;
        }

        // no captcha on this form (yet): never block the button
        if (!hasCaptcha(form)) {
            allow(true);
            if (hint) hint.hidden = true;
            return;
        }

        window["onCaptchaSolved_" + name] = function () { allow(true); };
        window["onCaptchaExpired_" + name] = function () { allow(false); };
        form._captchaAllow = allow;
        allow(false);
    });

    // Back button: the old ticks are gone, so ask again (only forms that have a captcha)
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