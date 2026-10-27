/* Theme switcher: opens the menu, changes <html data-theme>, remembers the choice.
   The new theme grows out of the place you clicked (View Transitions API);
   other browsers just fade the colours. */
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

        if (typeof document.startViewTransition === "function") {
            var radius = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
            root.classList.add("theme-vt");
            var transition = document.startViewTransition(apply);
            transition.ready.then(function () {
                root.animate(
                    { clipPath: ["circle(0px at " + x + "px " + y + "px)", "circle(" + radius + "px at " + x + "px " + y + "px)"] },
                    { duration: 750, easing: "cubic-bezier(.65, 0, .35, 1)", pseudoElement: "::view-transition-new(root)" }
                );
            }).catch(function () { /* animation not possible: the theme still changes */ });
            transition.finished.then(function () {
                root.classList.remove("theme-vt");
            }, function () {
                root.classList.remove("theme-vt");
            });
            return;
        }

        // no View Transitions: colours fade by themselves (CSS), the picture fades here
        apply();
        if (document.body.animate) {
            document.body.animate({ opacity: [0.35, 1] }, { duration: 450, easing: "ease-out" });
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
