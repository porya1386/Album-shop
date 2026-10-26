/* Login / register page: sliding panel, show-password buttons, password match.
   (The mobile menu is handled by header.js, which base.html already loads.) */
(function () {
    "use strict";

    var card = document.getElementById("auth-card");
    var overlay = document.getElementById("overlay");
    var paneLogin = document.getElementById("pane-login");
    var paneRegister = document.getElementById("pane-register");
    var ovLogin = document.getElementById("ov-login");
    var ovRegister = document.getElementById("ov-register");
    if (!card || !overlay || !paneLogin || !paneRegister || !ovLogin || !ovRegister) return;

    var TITLES = { login: "Log in | Jahan", register: "Register | Jahan" };

    // Show one of the two pages. Only the visible one can be reached with the keyboard.
    function setMode(mode, moveFocus) {
        card.setAttribute("data-mode", mode);
        document.title = TITLES[mode];

        var isLogin = mode === "login";
        paneLogin.inert = !isLogin;
        paneRegister.inert = isLogin;
        ovRegister.inert = !isLogin;
        ovLogin.inert = isLogin;
        paneLogin.setAttribute("aria-hidden", String(!isLogin));
        paneRegister.setAttribute("aria-hidden", String(isLogin));
        ovRegister.setAttribute("aria-hidden", String(!isLogin));
        ovLogin.setAttribute("aria-hidden", String(isLogin));

        if (moveFocus) {
            var first = (isLogin ? paneLogin : paneRegister).querySelector("input");
            if (first) first.focus({ preventScroll: true });
        }
    }

    // Keep the address bar in sync (#login / #register)
    function updateUrl(mode) {
        try {
            history.replaceState(null, "", location.pathname + location.search + "#" + mode);
        } catch (e) { /* not important */ }
    }

    function switchTo(mode) {
        setMode(mode, true);
        updateUrl(mode);
    }

    // Click anywhere on the sliding panel (or its button) to switch
    overlay.addEventListener("click", function () {
        switchTo(card.getAttribute("data-mode") === "login" ? "register" : "login");
    });

    // Text links used on phones
    Array.prototype.forEach.call(document.querySelectorAll("[data-switch]"), function (btn) {
        btn.addEventListener("click", function () {
            switchTo(this.getAttribute("data-switch"));
        });
    });

    // Which page to show first:  #register in the URL, else what the server says
    // (the server sends data-mode="register" after a failed registration), else login.
    var start = location.hash === "#register" ? "register"
              : location.hash === "#login" ? "login"
              : (card.getAttribute("data-mode") === "register" ? "register" : "login");
    setMode(start, false);

    // Show / hide password buttons
    Array.prototype.forEach.call(document.querySelectorAll(".pw-toggle"), function (btn) {
        btn.addEventListener("click", function () {
            var input = document.getElementById(this.getAttribute("aria-controls"));
            if (!input) return;
            var show = input.type === "password";
            input.type = show ? "text" : "password";
            this.textContent = show ? "Hide" : "Show";
            this.setAttribute("aria-pressed", String(show));
        });
    });

    // Both passwords must match
    var pass1 = document.getElementById("reg-password1");
    var pass2 = document.getElementById("reg-password2");
    if (pass1 && pass2) {
        var checkMatch = function () {
            pass2.setCustomValidity(pass2.value && pass1.value !== pass2.value ? "The two passwords do not match." : "");
        };
        pass1.addEventListener("input", checkMatch);
        pass2.addEventListener("input", checkMatch);
    }
})();