/* Change password page: show/hide password buttons + no double submit. */
(function () {
    "use strict";

    Array.prototype.forEach.call(document.querySelectorAll("[data-toggle-password]"), function (btn) {
        btn.addEventListener("click", function () {
            var input = document.getElementById(btn.dataset.togglePassword);
            if (!input) return;
            var show = input.type === "password";
            input.type = show ? "text" : "password";
            btn.setAttribute("aria-pressed", show ? "true" : "false");
            btn.setAttribute("aria-label", show ? "Hide password" : "Show password");
            input.focus();
        });
    });

    var form = document.querySelector("[data-pw-form]");
    if (!form) return;
    var submit = form.querySelector(".pw-submit");
    var label = submit ? submit.textContent : "";
    form.addEventListener("submit", function () {
        if (!submit) return;
        setTimeout(function () { submit.disabled = true; submit.textContent = "Saving..."; }, 0);
    });
    window.addEventListener("pageshow", function (e) {     // Back button
        if (e.persisted && submit) { submit.disabled = false; submit.textContent = label; }
    });
})();
