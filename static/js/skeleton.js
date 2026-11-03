/* Marks every  [data-skeleton]  box as done when its picture has loaded (or failed).
   Save as:  static/js/skeleton.js */
(function () {
    "use strict";

    function done(box) { box.classList.add("sk-done"); }

    function watch(box) {
        var imgs = box.querySelectorAll("img");
        if (!imgs.length) { done(box); return; }
        var left = imgs.length;
        function one() { left -= 1; if (left <= 0) done(box); }
        Array.prototype.forEach.call(imgs, function (img) {
            if (img.complete && img.naturalWidth > 0) { one(); return; }
            img.addEventListener("load", one, { once: true });
            img.addEventListener("error", one, { once: true });   // a broken picture must not shimmer forever
        });
    }

    function init() {
        Array.prototype.forEach.call(document.querySelectorAll("[data-skeleton]"), watch);
        // never leave a shimmer for ever (slow network)
        if (window.MutationObserver) {      // boxes added later by scripts (e.g. the copy of a moving row)
            new MutationObserver(function (list) {
                list.forEach(function (m) {
                    Array.prototype.forEach.call(m.addedNodes, function (n) {
                        if (n.nodeType !== 1) return;
                        if (n.matches && n.matches("[data-skeleton]")) watch(n);
                        if (n.querySelectorAll) Array.prototype.forEach.call(n.querySelectorAll("[data-skeleton]"), watch);
                    });
                });
            }).observe(document.body, { childList: true, subtree: true });
        }
        window.setTimeout(function () {
            Array.prototype.forEach.call(document.querySelectorAll("[data-skeleton]:not(.sk-done)"), done);
        }, 15000);
    }

    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
    else init();

    // coming back with the Back button: pictures are there already
    window.addEventListener("pageshow", function (e) {
        if (e.persisted) Array.prototype.forEach.call(document.querySelectorAll("[data-skeleton]"), done);
    });
})();