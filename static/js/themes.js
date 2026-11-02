/* Theme switcher: opens the menu, changes <html data-theme>, remembers the choice.
   The new theme grows out of the place you clicked (a round hole in the old painting).
   Load backgrounds.css too: it has the .theme-reveal rules. */
(function () {
    "use strict";

    var KEY = "jahan-theme";
    var root = document.documentElement;
    var box = document.querySelector("[data-theme-switch]");
    if (!box) return;

    var button = box.querySelector(".theme-btn");
    var menu = box.querySelector(".theme-menu");
    var items = Array.prototype.slice.call(menu.querySelectorAll("[data-theme-choice]"));
    var names = items.map(function (i) { return i.getAttribute("data-theme-choice"); });
    // the variables that make the painting of the OLD theme (copied to the overlay)
    var COPY_VARS = ["--night", "--bg-land", "--bg-port", "--bg-veil", "--bg-gradient"];
    var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function current() {
        var t = root.getAttribute("data-theme");
        return names.indexOf(t) > -1 ? t : names[0];
    }

    function mark() {
        var now = current();
        items.forEach(function (item) {
            item.setAttribute("aria-checked", item.getAttribute("data-theme-choice") === now ? "true" : "false");
        });
    }

    function save(theme) {
        try { localStorage.setItem(KEY, theme); } catch (e) { /* private mode: not important */ }
    }

    function change(theme, x, y) {
        if (theme === current()) return;

        function apply() {
            root.setAttribute("data-theme", theme);
            mark();
            save(theme);
        }

        if (reduceMotion) { apply(); return; }

        // The colours fade (class theme-fade, see themes.css). The old painting stays on top for a
        // moment and a round hole grows out of the place you clicked, showing the new painting.
        // (No View Transitions on purpose: they turn the page into a picture, and the blur of the
        // header and cards gets weaker until the animation ends.)
        var cs = getComputedStyle(root);
        var overlay = document.createElement("div");
        overlay.className = "theme-reveal";
        overlay.setAttribute("aria-hidden", "true");
        COPY_VARS.forEach(function (name) {
            var value = cs.getPropertyValue(name);
            if (value && value.trim()) overlay.style.setProperty(name, value.trim());
        });
        overlay.style.setProperty("--reveal-x", x + "px");
        overlay.style.setProperty("--reveal-y", y + "px");
        document.body.appendChild(overlay);

        root.classList.add("theme-fade");
        apply();

        var radius = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y)) + 4;
        var done = function () {
            overlay.remove();
            root.classList.remove("theme-fade");
        };

        if (overlay.animate && window.CSS && CSS.supports && CSS.supports("mask-image", "radial-gradient(circle, red, blue)")) {
            var run = overlay.animate(
                { "--reveal-r": ["0px", radius + "px"] },
                { duration: 1050, easing: "cubic-bezier(.65, 0, .35, 1)" }
            );
            run.finished.then(done, done);
        } else if (overlay.animate) {
            overlay.animate({ opacity: [1, 0] }, { duration: 700, easing: "ease-out" }).finished.then(done, done);
        } else {
            setTimeout(done, 800);
        }
    }

    /* ---- menu open / close ---- */
    function openMenu() {
        menu.hidden = false;
        button.setAttribute("aria-expanded", "true");
        var checked = menu.querySelector('[aria-checked="true"]') || items[0];
        if (checked) checked.focus();
    }
    function closeMenu(returnFocus) {
        menu.hidden = true;
        button.setAttribute("aria-expanded", "false");
        if (returnFocus) button.focus();
    }

    button.addEventListener("click", function () {
        if (menu.hidden) openMenu(); else closeMenu(false);
    });

    items.forEach(function (item) {
        item.addEventListener("click", function (e) {
            // keyboard "click" has no position: grow from the button instead
            var rect = button.getBoundingClientRect();
            var x = e.clientX || rect.left + rect.width / 2;
            var y = e.clientY || rect.top + rect.height / 2;
            change(item.getAttribute("data-theme-choice"), x, y);
        });
    });

    document.addEventListener("click", function (e) {
        if (!menu.hidden && !box.contains(e.target)) closeMenu(false);
    });

    box.addEventListener("keydown", function (e) {
        if (menu.hidden) return;
        var i = items.indexOf(document.activeElement);
        if (e.key === "Escape") { e.preventDefault(); closeMenu(true); }
        else if (e.key === "ArrowDown") { e.preventDefault(); items[(i + 1) % items.length].focus(); }
        else if (e.key === "ArrowUp") { e.preventDefault(); items[(i - 1 + items.length) % items.length].focus(); }
        else if (e.key === "Tab") { closeMenu(false); }
    });

    /* another tab changed the theme */
    window.addEventListener("storage", function (e) {
        if (e.key === KEY && e.newValue && names.indexOf(e.newValue) > -1) {
            root.setAttribute("data-theme", e.newValue);
            mark();
        }
    });

    mark();
})();