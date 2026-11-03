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

    // Elements that have their OWN painting (not the page background) cannot be reached by the big
    // overlay. For each of them we put a copy of the OLD painting inside (a "ghost") with the same round
    // hole that grows from the click, so everything changes together.
    // Add  data-theme-art  to any element that should do this. The login card panel is included.
    var GHOST_SELECTOR = "[data-theme-art], .auth-card .overlay";

    function makeGhosts(x, y) {
        var list = [];
        Array.prototype.forEach.call(document.querySelectorAll(GHOST_SELECTOR), function (el) {
            var rect = el.getBoundingClientRect();
            if (!rect.width || !rect.height) return;
            var cs = getComputedStyle(el);
            var ghost = document.createElement("span");
            ghost.setAttribute("aria-hidden", "true");
            ghost.style.cssText =
                "position:absolute;inset:0;z-index:-1;pointer-events:none;border-radius:inherit;" +
                "background-image:" + cs.backgroundImage + ";" +
                "background-size:" + cs.backgroundSize + ";" +
                "background-position:" + cs.backgroundPosition + ";" +
                "background-repeat:" + cs.backgroundRepeat + ";" +
                "background-color:" + cs.backgroundColor + ";";
            var cx = (x - rect.left) + "px", cy = (y - rect.top) + "px";
            var mask = "radial-gradient(circle at " + cx + " " + cy +
                       ", transparent var(--reveal-r), #000 calc(var(--reveal-r) + 2px))";
            ghost.style.webkitMaskImage = mask;
            ghost.style.maskImage = mask;
            ghost.style.setProperty("--reveal-r", "0px");

            var oldIsolation = el.style.isolation;
            el.style.isolation = "isolate";             // so z-index:-1 stays inside the panel, above its own background
            el.insertBefore(ghost, el.firstChild);
            list.push({
                el: ghost,
                remove: function () { ghost.remove(); el.style.isolation = oldIsolation; }
            });
        });
        return list;
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

        // panels that carry their own painting (the sliding panel of the login card) get the same round reveal
        var ghosts = makeGhosts(x, y);

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
            ghosts.forEach(function (g) {
                g.el.animate({ "--reveal-r": ["0px", radius + "px"] },
                             { duration: 1050, easing: "cubic-bezier(.65, 0, .35, 1)" }).finished.then(g.remove, g.remove);
            });
        } else if (overlay.animate) {
            overlay.animate({ opacity: [1, 0] }, { duration: 700, easing: "ease-out" }).finished.then(done, done);
            ghosts.forEach(function (g) {
                g.el.animate({ opacity: [1, 0] }, { duration: 700, easing: "ease-out" }).finished.then(g.remove, g.remove);
            });
        } else {
            setTimeout(done, 800);
            ghosts.forEach(function (g) { setTimeout(g.remove, 800); });
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