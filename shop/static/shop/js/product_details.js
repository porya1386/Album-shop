(function () {
    "use strict";

    /* ---------- Full size image viewer ---------- */
    const zoom = document.getElementById("pd-zoom");
    const openBtn = document.getElementById("pd-zoom-open");
    const closeBtn = document.getElementById("pd-zoom-close");

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

        // Click anywhere on the image or the dark backdrop closes it
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
                // Fallback for browsers/contexts without clipboard access
                window.prompt("Copy this link:", window.location.href);
                return;
            }
            setTimeout(function () {
                copyBtn.textContent = original;
            }, 2000);
        });
    }
})();
