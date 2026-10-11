(function () {
    "use strict";

    // Touch-only devices have no cursor to follow
    if (window.matchMedia("(hover: none)").matches) return;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const EASE = reduceMotion ? 1 : 0.12;     // 1 = jump instantly, smaller = softer trailing

    function init() {
        // Safe to load twice (e.g. in base.html AND in a page): only one glow is created
        if (document.querySelector(".mouse-glow")) return;

        const glow = document.createElement("div");
        glow.className = "mouse-glow";
        glow.setAttribute("aria-hidden", "true");
        document.body.appendChild(glow);

        let half = glow.offsetWidth / 2;
        let x = 0, y = 0;                         // where the glow is now
        let tx = 0, ty = 0;                       // where the mouse is
        let raf = 0;
        let placed = false;

        function draw() {
            x += (tx - x) * EASE;
            y += (ty - y) * EASE;
            glow.style.transform = "translate3d(" + (x - half) + "px," + (y - half) + "px,0)";

            if (Math.abs(tx - x) > 0.2 || Math.abs(ty - y) > 0.2) {
                raf = requestAnimationFrame(draw);
            } else {
                raf = 0;
            }
        }

        window.addEventListener("pointermove", function (e) {
            if (e.pointerType === "touch") return;
            tx = e.clientX;
            ty = e.clientY;
            if (!placed) { x = tx; y = ty; placed = true; }   // first move: appear under the cursor
            glow.classList.add("is-on");
            if (!raf) raf = requestAnimationFrame(draw);
        }, { passive: true });

        // Fade out when the mouse leaves the window
        document.documentElement.addEventListener("mouseleave", function () {
            glow.classList.remove("is-on");
        });

        window.addEventListener("resize", function () {
            half = glow.offsetWidth / 2;
        });
    }

    // Works whether the script is in <head> (with defer) or at the end of <body>
    if (document.body) init();
    else document.addEventListener("DOMContentLoaded", init);
})();
