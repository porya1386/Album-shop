/* Home page: reveal on scroll, typed sentence, soft parallax on the hero picture.
   Save as:  website/static/website/js/home.js */
(function () {
    "use strict";
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    // reveal on scroll
    var els = document.querySelectorAll(".hm-reveal");
    if ("IntersectionObserver" in window) {
        var io = new IntersectionObserver(function (list) {
            list.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
        }, { threshold: 0.12, rootMargin: "0px 0px -6% 0px" });
        Array.prototype.forEach.call(els, function (el) { io.observe(el); });
    } else {
        Array.prototype.forEach.call(els, function (el) { el.classList.add("in"); });
    }

    // the sentence types itself when it comes into view
    var t = document.querySelector("[data-hm-type]");
    if (t && !reduce && "IntersectionObserver" in window) {
        var full = t.getAttribute("data-hm-type"), chars = Array.from(full);
        var h = t.offsetHeight;                       // keep the height so the page does not jump
        t.style.minHeight = h + "px";
        t.textContent = "";
        var tio = new IntersectionObserver(function (list) {
            if (!list[0].isIntersecting) return;
            tio.disconnect();
            var i = 0;
            t.classList.add("typing");
            (function step() {
                t.textContent = chars.slice(0, ++i).join("");
                if (i < chars.length) setTimeout(step, 48);
                else setTimeout(function () { t.classList.remove("typing"); }, 1800);
            })();
        }, { threshold: 0.6 });
        tio.observe(t);
    }

})();