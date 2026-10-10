(function () {
    "use strict";

    /* ---------- Elements ---------- */
    const mainImg = document.getElementById("pd-main-img");
    const zoom = document.getElementById("pd-zoom");
    const zoomImg = document.getElementById("pd-zoom-img");
    const openBtn = document.getElementById("pd-zoom-open");
    const closeBtn = document.getElementById("pd-zoom-close");
    const prevBtn = document.getElementById("pd-prev");
    const nextBtn = document.getElementById("pd-next");
    const thumbsBox = document.getElementById("pd-thumbs");
    const thumbs = Array.from(document.querySelectorAll(".pd-thumb"));

    /* ---------- Gallery ---------- */
    let index = 0;

    function show(i) {
        if (thumbs.length < 2) return;

        index = (i + thumbs.length) % thumbs.length;   // wrap around
        const t = thumbs[index];

        mainImg.src = t.dataset.src;
        mainImg.alt = t.dataset.alt;
        if (zoomImg) {
            zoomImg.src = t.dataset.src;
            zoomImg.alt = t.dataset.alt;
        }

        thumbs.forEach(function (el, n) {
            el.classList.toggle("is-active", n === index);
        });

        // Scroll only the thumbnail strip, never the whole page
        if (thumbsBox) {
            const target = t.offsetLeft - (thumbsBox.clientWidth - t.offsetWidth) / 2;
            thumbsBox.scrollTo({ left: target, behavior: "smooth" });
        }
    }

    if (thumbs.length > 1) {
        if (prevBtn) prevBtn.addEventListener("click", function () { show(index - 1); });
        if (nextBtn) nextBtn.addEventListener("click", function () { show(index + 1); });

        thumbs.forEach(function (el, n) {
            el.addEventListener("click", function () { show(n); });
        });

        // Keyboard arrows (also work while the full size viewer is open)
        document.addEventListener("keydown", function (e) {
            if (e.key === "ArrowLeft") show(index - 1);
            if (e.key === "ArrowRight") show(index + 1);
        });

        // Swipe on touch screens
        let startX = 0;
        openBtn.addEventListener("touchstart", function (e) {
            startX = e.changedTouches[0].clientX;
        }, { passive: true });
        openBtn.addEventListener("touchend", function (e) {
            const dx = e.changedTouches[0].clientX - startX;
            if (Math.abs(dx) > 50) show(dx < 0 ? index + 1 : index - 1);
        }, { passive: true });
    }

    /* ---------- Full size viewer ---------- */
    function openZoom() {
        if (typeof zoom.showModal === "function") zoom.showModal();
        else zoom.setAttribute("open", "");
    }

    function closeZoom() {
        if (typeof zoom.close === "function") zoom.close();
        else zoom.removeAttribute("open");
    }

    if (zoom && openBtn) {
        openBtn.addEventListener("click", openZoom);
        if (closeBtn) closeBtn.addEventListener("click", closeZoom);

        // Click on the image or the dark backdrop closes it
        zoom.addEventListener("click", closeZoom);
    }

    /* ---------- Copy link button ---------- */
    const copyBtn = document.getElementById("pd-copy");

    if (copyBtn) {
        const original = copyBtn.textContent;

        copyBtn.addEventListener("click", async function () {
            try {
                await navigator.clipboard.writeText(window.location.href);
                copyBtn.textContent = "Link copied!";
            } catch (err) {
                window.prompt("Copy this link:", window.location.href);
                return;
            }
            setTimeout(function () {
                copyBtn.textContent = original;
            }, 2000);
        });
    }
})();
