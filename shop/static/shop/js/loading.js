/* Loading states.
   1) Product images: shimmer until loaded, then fade in (list + details page).
   2) Search: spinner in the button + skeleton cards, then the request is sent.
   If this script fails, nothing is hidden. */
(function () {
    "use strict";

    // ---- the only settings ----
    var MIN_SHOW = 600;       // ms: image shimmer stays at least this long (0 = only while really loading)
    var SEARCH_DELAY = 500;   // ms: spinner + skeletons show this long before the search is sent (0 = send at once)
    // On the live server you can lower both (e.g. 300 / 300) or set them to 0.
    var TIMEOUT = 10000;      // never keep an image placeholder longer than this

    /* ---------- 1) images ---------- */
    function watch(img, host) {
        if (!img || !host) return;
        var loaded = img.complete && img.naturalWidth > 0;
        if (loaded && !MIN_SHOW) { host.classList.remove("is-loading"); return; }

        host.classList.add("is-loading");
        var started = Date.now();
        var finished = false;
        function done() {
            if (finished) return;
            finished = true;
            img.removeEventListener("load", done);
            img.removeEventListener("error", done);
            var wait = Math.max(0, MIN_SHOW - (Date.now() - started));
            setTimeout(function () { host.classList.remove("is-loading"); }, wait);
        }
        if (loaded) { done(); return; }
        img.addEventListener("load", done);
        img.addEventListener("error", done);
        setTimeout(done, TIMEOUT);
    }

    function watchAll(root) {
        Array.prototype.forEach.call(
            root.querySelectorAll(".frame > img, .pd-frame img, .pd-thumb img"),
            function (img) { watch(img, img.closest(".frame, .pd-frame, .pd-thumb")); }
        );
    }
    watchAll(document);

    /* the gallery changes the big image's src: show the shimmer again for that */
    var big = document.querySelector(".pd-frame img");
    if (big && "MutationObserver" in window) {
        new MutationObserver(function () { watch(big, big.closest(".pd-frame")); })
            .observe(big, { attributes: true, attributeFilter: ["src"] });
    }

    /* ---------- 2) search ---------- */
    var form = document.getElementById("filter-form");
    var grid = document.getElementById("grid");
    if (!form || !grid) return;

    var button = form.querySelector('button[type="submit"]');
    var original = grid.innerHTML;
    var busy = false;

    function skeletons(n) {
        var card =
            '<article class="product product--skeleton" aria-hidden="true">' +
            '<div class="frame sk"></div>' +
            '<div class="product-info">' +
            '<div class="sk sk-line sk-title"></div><div class="sk sk-line sk-meta"></div>' +
            '<div class="sk sk-line"></div>' +
            '<div class="sk-foot"><div class="sk sk-line sk-price"></div><div class="sk sk-pill"></div></div>' +
            '</div></article>';
        return new Array(n + 1).join(card);
    }

    function setBusy(state) {
        busy = state;
        grid.setAttribute("aria-busy", state ? "true" : "false");
        if (!button) return;
        var old = button.querySelector(".spinner");
        if (old) old.parentNode.removeChild(old);
        button.classList.toggle("is-busy", state);
        if (state) button.insertAdjacentHTML("afterbegin", '<span class="spinner" aria-hidden="true"></span>');
    }

    form.addEventListener("submit", function (e) {
        if (busy) { e.preventDefault(); return; }
        setBusy(true);
        grid.innerHTML = skeletons(6);
        if (SEARCH_DELAY > 0) {
            e.preventDefault();                       // let the animation play, then send the form
            setTimeout(function () { form.submit(); }, SEARCH_DELAY);
        }
        if (button) setTimeout(function () { button.disabled = true; }, 0);
    });

    /* Back button (bfcache) must not show the old spinner/skeletons */
    window.addEventListener("pageshow", function (e) {
        if (!e.persisted) return;
        setBusy(false);
        grid.innerHTML = original;
        if (button) button.disabled = false;
        watchAll(grid);
    });
})();