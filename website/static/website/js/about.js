/* About page: the two boxes (story and "At a glance") and every heading fade in softly while you scroll.
   Save as:  website/static/website/js/about.js
   No libraries, no CSS needed. Without JavaScript (or with "reduce motion") the page is simply shown. */
(function () {
    "use strict";

    if (!("IntersectionObserver" in window) || !Element.prototype.animate) return;
    if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    var targets = Array.prototype.slice.call(
        document.querySelectorAll(".about-grid .panel, .about-grid .story h2, .about-grid .pullquote, .about-grid blockquote")
    );
    if (!targets.length) return;

    var seen = new WeakSet();

    var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (!entry.isIntersecting || seen.has(entry.target)) return;
            seen.add(entry.target);
            observer.unobserve(entry.target);
            entry.target.style.opacity = "";                 // show it, then play the movement
            entry.target.animate(
                [{ opacity: 0, transform: "translateY(22px)" }, { opacity: 1, transform: "none" }],
                { duration: 650, easing: "cubic-bezier(.2, .7, .2, 1)" }
            );
        });
    }, { threshold: 0.12, rootMargin: "0px 0px -6% 0px" });

    targets.forEach(function (el) {
        var rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight * 0.9) return;     // already on screen: leave it
        el.style.opacity = "0";                              // hidden until it scrolls into view
        observer.observe(el);
    });

    // safety: never leave anything hidden (e.g. if the browser skips the observer)
    window.setTimeout(function () {
        targets.forEach(function (el) { if (!seen.has(el)) el.style.opacity = ""; });
    }, 8000);
})();