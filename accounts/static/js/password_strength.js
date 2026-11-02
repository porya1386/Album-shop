/* Password strength bar.
   Save as:  static/js/password_strength.js

   Markup (see login.html):
     <input type="password" data-strength ...>
     <div class="pw-meter" data-strength-for="ID-OF-THE-INPUT"
          data-label-0="..." data-label-1="..." ... data-label-4="..."> <div class="pw-meter-bar"></div> </div>
     <p class="pw-meter-text" id="..."></p>
   The bar fills from 0 while the person types: red -> orange -> yellow -> green.
   It is only a help for the visitor. The real rules are checked by Django on the server. */
(function () {
    "use strict";

    var COMMON = [
        "password", "passw0rd", "qwerty", "qwertyuiop", "asdfgh", "zxcvbn", "letmein", "welcome",
        "admin", "iloveyou", "monkey", "dragon", "football", "abc123", "111111", "123123",
        "000000", "login", "master", "sunshine", "princess", "shadow", "football", "baseball"
    ];
    var SEQUENCES = ["abcdefghijklmnopqrstuvwxyz", "0123456789", "qwertyuiopasdfghjklzxcvbnm", "9876543210"];
    var MAX_BITS = 72;                 // bar is full at this strength

    function hasSequence(text) {
        var lower = text.toLowerCase();
        for (var s = 0; s < SEQUENCES.length; s += 1) {
            for (var i = 0; i + 3 <= SEQUENCES[s].length; i += 1) {
                if (lower.indexOf(SEQUENCES[s].substr(i, 4)) > -1) return true;
            }
        }
        return false;
    }

    /* returns {bits, short}  bits ~ how hard it is to guess */
    function measure(password, personal) {
        var len = password.length;
        if (!len) return { bits: 0, short: false };

        var pool = 0;
        if (/[a-z]/.test(password)) pool += 26;
        if (/[A-Z]/.test(password)) pool += 26;
        if (/[0-9]/.test(password)) pool += 10;
        if (/[^\w\s]|_/.test(password)) pool += 33;
        if (/\s/.test(password)) pool += 1;
        if (/[^\x00-\x7F]/.test(password)) pool += 60;            // other alphabets (Persian ...)

        var unique = {};
        password.split("").forEach(function (c) { unique[c] = 1; });
        var uniqueCount = Object.keys(unique).length;

        var bits = len * Math.log(Math.max(pool, 2)) / Math.LN2;

        // the same few characters again and again
        bits *= Math.min(1, 0.45 + uniqueCount / len * 0.55);
        if (/(.)\1{2,}/.test(password)) bits *= 0.75;               // aaa, 1111
        if (hasSequence(password)) bits *= 0.7;                     // abcd, 1234, qwer

        var lower = password.toLowerCase();
        if (COMMON.some(function (w) { return lower.indexOf(w) > -1; })) bits = Math.min(bits, 18);
        if (/^\d+$/.test(password)) bits = Math.min(bits, 22);      // only digits

        // name or e-mail inside the password
        personal.forEach(function (word) {
            if (word && word.length >= 3 && lower.indexOf(word.toLowerCase()) > -1) bits = Math.min(bits, 20);
        });

        return { bits: bits, short: len < 8 };
    }

    function levelOf(result) {
        if (!result.bits) return 0;
        if (result.short || result.bits < 28) return 1;   // weak
        if (result.bits < 40) return 2;                   // fair
        if (result.bits < 56) return 3;                   // good
        return 4;                                         // strong
    }

    function setup(input) {
        var meter = document.querySelector('[data-strength-for="' + input.id + '"]');
        if (!meter) return;
        var bar = meter.querySelector(".pw-meter-bar");
        var text = document.getElementById(meter.getAttribute("data-text")) ||
                   meter.parentNode.querySelector(".pw-meter-text");
        var personalIds = (meter.getAttribute("data-personal") || "").split(",");

        function personal() {
            var out = [];
            personalIds.forEach(function (id) {
                var el = id && document.getElementById(id.trim());
                if (el && el.value) {
                    out.push(el.value.split("@")[0]);
                }
            });
            return out;
        }

        function update() {
            var result = measure(input.value, personal());
            var level = levelOf(result);
            var percent = result.bits ? Math.max(6, Math.min(100, result.bits / MAX_BITS * 100)) : 0;
            if (level === 1) percent = Math.min(percent, 30);
            if (level === 2) percent = Math.min(Math.max(percent, 32), 55);
            if (level === 3) percent = Math.min(Math.max(percent, 56), 80);
            if (level === 4) percent = Math.max(percent, 82);

            bar.style.width = percent + "%";
            meter.setAttribute("data-level", String(level));
            meter.setAttribute("aria-valuenow", String(Math.round(percent)));
            if (text) {
                text.textContent = result.short && input.value
                    ? (meter.getAttribute("data-label-short") || "")
                    : (meter.getAttribute("data-label-" + level) || "");
            }
        }

        input.addEventListener("input", update);
        personalIds.forEach(function (id) {
            var el = id && document.getElementById(id.trim());
            if (el) el.addEventListener("input", update);
        });
        update();
    }

    Array.prototype.forEach.call(document.querySelectorAll("input[data-strength]"), setup);

    /* Repeat-password bar: fills while what you type is the start of the first
       password, turns green + a tick when equal, red when it differs. */
    function setupMatch(meter) {
        var second = document.getElementById(meter.getAttribute("data-match-for"));
        var first = document.getElementById(meter.getAttribute("data-match-with"));
        var bar = meter.querySelector(".pw-meter-bar");
        var text = document.getElementById(meter.getAttribute("data-text"));
        if (!second || !first) return;

        function update() {
            var a = first.value, b = second.value, state = "0", percent = 0, label = "";
            if (b) {
                if (a === b) { state = "ok"; percent = 100; label = "ok"; }
                else if (a.indexOf(b) === 0) { state = "partial"; percent = Math.max(8, b.length / a.length * 100); label = "partial"; }
                else { state = "bad"; percent = 100; label = "bad"; }
            }
            bar.style.width = percent + "%";
            meter.setAttribute("data-match", state);
            if (text) {
                text.setAttribute("data-match", state);
                text.textContent = label ? (text.getAttribute("data-label-" + label) || "") : "";
            }
        }
        second.addEventListener("input", update);
        first.addEventListener("input", update);
        update();
    }
    Array.prototype.forEach.call(document.querySelectorAll("[data-match-for]"), setupMatch);
})();