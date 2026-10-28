/* Password pages: show/hide password buttons + no double submit.
   The texts come from data-* attributes on the <form data-pw-form>
   (the template translates them). */
(function () {
    "use strict";

    var form = document.querySelector("[data-pw-form]");
    var SHOW = (form && form.dataset.showLabel) || "Show password";
    var HIDE = (form && form.dataset.hideLabel) || "Hide password";
    var SAVING = (form && form.dataset.savingText) || "Saving...";

    Array.prototype.forEach.call(document.querySelectorAll("[data-toggle-password]"), function (btn) {
        btn.addEventListener("click", function () {
            var input = document.getElementById(btn.dataset.togglePassword);
            if (!input) return;
            var show = input.type === "password";
            input.type = show ? "text" : "password";
            btn.setAttribute("aria-pressed", show ? "true" : "false");
            btn.setAttribute("aria-label", show ? HIDE : SHOW);
            input.focus();
        });
    });

    if (!form) return;
    var submit = form.querySelector(".pw-submit");
    var label = submit ? submit.textContent : "";
    form.addEventListener("submit", function () {
        if (!submit) return;
        setTimeout(function () { submit.disabled = true; submit.textContent = SAVING; }, 0);
    });
    window.addEventListener("pageshow", function (e) {     // Back button
        if (e.persisted && submit) { submit.disabled = false; submit.textContent = label; }
    });
})();