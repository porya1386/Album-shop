(function () {
    "use strict";

    const viewport = document.getElementById("marquee-viewport");
    const track = document.getElementById("marquee-track");
    const group = document.getElementById("marquee-group");
    if (!viewport || !track || !group || group.children.length === 0) return;

    const SPEED = 45;                       // pixels per second (lower = slower)
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

    function removeClones() {
        track.querySelectorAll("[data-clone]").forEach(function (el) { el.remove(); });
    }

    // Repeat the list until it is wider than the screen, then slide by exactly
    // one list-width: when the animation restarts it looks identical = no jump.
    function build() {
        removeClones();
        if (reduceMotion.matches) return;           // CSS turns the animation off

        const groupWidth = group.getBoundingClientRect().width;
        const viewWidth = viewport.clientWidth;
        if (!groupWidth || !viewWidth) return;

        const total = Math.ceil(viewWidth / groupWidth) + 1;   // groups incl. the original
        for (let i = 1; i < total; i++) {
            const copy = group.cloneNode(true);
            copy.removeAttribute("id");
            copy.setAttribute("aria-hidden", "true");
            copy.setAttribute("data-clone", "");
            copy.querySelectorAll("a").forEach(function (a) { a.tabIndex = -1; });
            track.appendChild(copy);
        }

        track.style.setProperty("--shift", groupWidth + "px");
        track.style.setProperty("--dur", (groupWidth / SPEED) + "s");
    }

    // Rebuild when the width changes (resize / rotate phone)
    let lastWidth = -1;
    let timer = 0;
    function onResize() {
        const w = viewport.clientWidth;
        if (Math.abs(w - lastWidth) < 1) return;
        lastWidth = w;
        clearTimeout(timer);
        timer = setTimeout(build, 150);
    }

    build();
    lastWidth = viewport.clientWidth;

    if (typeof ResizeObserver === "function") {
        new ResizeObserver(onResize).observe(viewport);
    } else {
        window.addEventListener("resize", onResize);
    }
    if (typeof reduceMotion.addEventListener === "function") {
        reduceMotion.addEventListener("change", build);
    }

    // Coming back with the Back button can restore the page from the browser's
    // back/forward cache: drop the mouse-click focus and restart the animation.
    window.addEventListener("pageshow", function (e) {
        if (!e.persisted) return;

        const active = document.activeElement;
        if (active && viewport.contains(active) && !active.matches(":focus-visible")) {
            active.blur();
        }

        build();
        track.style.animation = "none";
        void track.offsetWidth;               // force a reflow so the restart sticks
        track.style.animation = "";
    });
})();
