(function () {
    "use strict";

    if (!document.querySelector(".like-btn")) return;

    /* Show the new state. `animateCount` makes the number slide in. */
    function setState(btn, liked, count, animateCount) {
        btn.classList.toggle("is-liked", liked);
        btn.setAttribute("aria-pressed", liked ? "true" : "false");

        const el = btn.querySelector(".like-count");
        if (el && String(el.textContent) !== String(count)) {
            el.textContent = count;
            if (animateCount) {
                el.classList.remove("bump");
                void el.offsetWidth;                  // restart the animation
                el.classList.add("bump");
            }
        }
    }

    /* Heart pop + ring + flying dots */
    function playPop(btn) {
        btn.classList.remove("pop");
        void btn.offsetWidth;
        btn.classList.add("pop");

        const box = btn.querySelector(".like-burst");
        if (!box) return;

        box.textContent = "";
        const DOTS = 7;
        for (let i = 0; i < DOTS; i++) {
            const dot = document.createElement("i");
            dot.style.setProperty("--a", (i * 360 / DOTS) + "deg");
            box.appendChild(dot);
        }
        setTimeout(function () { box.textContent = ""; }, 700);
    }

    async function toggle(btn) {
        // Not logged in: go to the login page and come back afterwards
        if (btn.dataset.loginUrl) {
            window.location.href = btn.dataset.loginUrl;
            return;
        }
        if (btn.dataset.busy === "1") return;         // ignore clicks while saving
        btn.dataset.busy = "1";

        const countEl = btn.querySelector(".like-count");
        const wasLiked = btn.classList.contains("is-liked");
        const before = parseInt(countEl.textContent, 10) || 0;

        // Update immediately so it feels instant; the server answer corrects it
        setState(btn, !wasLiked, Math.max(0, before + (wasLiked ? -1 : 1)), true);
        if (!wasLiked) playPop(btn);

        try {
            const res = await fetch(btn.dataset.url, {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "X-CSRFToken": btn.dataset.csrf,
                    "X-Requested-With": "XMLHttpRequest",
                    "Accept": "application/json"
                }
            });

            if (res.status === 401) {                 // session expired
                setState(btn, wasLiked, before, false);
                let data = {};
                try { data = await res.json(); } catch (e) { /* ignore */ }
                window.location.href = (data.login_url || "/") +
                    "?next=" + encodeURIComponent(window.location.pathname + window.location.search);
                return;
            }
            if (!res.ok) throw new Error("HTTP " + res.status);

            const data = await res.json();
            setState(btn, !!data.liked, data.count, false);
        } catch (err) {
            setState(btn, wasLiked, before, false);   // something failed: undo
        } finally {
            delete btn.dataset.busy;
        }
    }

    // One listener for every like button on the page
    document.addEventListener("click", function (e) {
        const btn = e.target.closest(".like-btn");
        if (btn) toggle(btn);
    });
})();
