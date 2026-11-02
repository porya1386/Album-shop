/* Blog: like button (no page reload) + "are you sure" on deleting a comment.
   Save as: blogs/static/blogs/js/blog.js */
(function () {
    "use strict";

    // wraps the heart and adds the little hearts / ring that fly out when you like
    function decorate(like) {
        var icon = like.querySelector(".icon");
        if (!icon || like.querySelector(".blog-like-icon")) return;
        var wrap = document.createElement("span");
        wrap.className = "blog-like-icon";
        icon.parentNode.insertBefore(wrap, icon);
        wrap.appendChild(icon);

        var burst = document.createElement("span");
        burst.className = "blog-burst";
        burst.setAttribute("aria-hidden", "true");
        for (var i = 0; i < 8; i += 1) {
            var dot = document.createElement("i");
            dot.style.setProperty("--a", (i * 45) + "deg");
            burst.appendChild(dot);
        }
        wrap.appendChild(burst);
    }

    function setup(like) {
        var busy = false;
        decorate(like);
        like.addEventListener("click", function (e) {
            e.preventDefault();
            var loginUrl = like.getAttribute("data-login-url");
            if (loginUrl) { window.location.href = loginUrl; return; }     // not logged in -> login page
            if (busy) return;
            busy = true;

            fetch(like.getAttribute("data-url"), {
                method: "POST",
                headers: { "X-CSRFToken": like.getAttribute("data-csrf"), "X-Requested-With": "XMLHttpRequest" },
                credentials: "same-origin"
            })
                .then(function (r) {
                    if (r.status === 401) return r.json().then(function (d) { window.location.href = d.login_url || "/"; return null; });
                    if (!r.ok) throw new Error("bad status");
                    return r.json();
                })
                .then(function (data) {
                    if (!data) return;
                    like.classList.toggle("is-liked", data.liked);
                    like.setAttribute("aria-pressed", data.liked ? "true" : "false");
                    like.querySelector(".blog-like-count").textContent = data.count;
                    if (data.liked) {
                        like.classList.remove("pop");
                        void like.offsetWidth;            // restart the animation
                        like.classList.add("pop");
                    }
                })
                .catch(function () { /* network problem: leave the button as it was */ })
                .then(function () { busy = false; });
        });
    }
    Array.prototype.forEach.call(document.querySelectorAll(".blog-like"), setup);

    Array.prototype.forEach.call(document.querySelectorAll("[data-confirm]"), function (btn) {
        btn.addEventListener("click", function (e) {
            if (!window.confirm(btn.getAttribute("data-confirm"))) e.preventDefault();
        });
    });
})();