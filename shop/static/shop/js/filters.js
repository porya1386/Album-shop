/* Products filter: dual price slider synced with the number inputs,
   mobile "Filters" toggle. Without JS the plain form still works. */
(function () {
    "use strict";
    document.documentElement.classList.add("has-js");

    var box = document.querySelector("[data-range]");
    var panel = document.getElementById("filters");
    if (!box || !panel) return;

    var LO = parseInt(panel.dataset.min, 10) || 0;
    var HI = parseInt(panel.dataset.max, 10) || 0;
    var track = box.querySelector("[data-track]");
    var fill = box.querySelector("[data-fill]");
    var sMin = box.querySelector("[data-range-min]");
    var sMax = box.querySelector("[data-range-max]");
    var nMin = box.querySelector('input[name="min_price"]');
    var nMax = box.querySelector('input[name="max_price"]');

    /* slider only makes sense when there is a real range */
    if (HI > LO && track && nMin && nMax) {
        track.hidden = false;

        function num(input, fallback) {
            var v = parseFloat(input.value);
            return isNaN(v) ? fallback : v;
        }
        function paint() {
            var a = (sMin.value - LO) / (HI - LO) * 100;
            var b = (sMax.value - LO) / (HI - LO) * 100;
            fill.style.left = a + "%";
            fill.style.width = Math.max(0, b - a) + "%";
        }
        function fromInputs() {
            sMin.value = Math.min(Math.max(num(nMin, LO), LO), HI);
            sMax.value = Math.min(Math.max(num(nMax, HI), LO), HI);
            paint();
        }
        sMin.addEventListener("input", function () {
            if (+sMin.value > +sMax.value) sMin.value = sMax.value;
            nMin.value = +sMin.value <= LO ? "" : sMin.value;   // untouched end = no filter
            paint();
        });
        sMax.addEventListener("input", function () {
            if (+sMax.value < +sMin.value) sMax.value = sMin.value;
            nMax.value = +sMax.value >= HI ? "" : sMax.value;
            paint();
        });
        nMin.addEventListener("input", fromInputs);
        nMax.addEventListener("input", fromInputs);
        fromInputs();
    }

    /* mobile toggle; stay open if a price filter is already active */
    var toggle = document.querySelector("[data-filters-toggle]");
    if (toggle) {
        function setOpen(open) {
            panel.classList.toggle("is-open", open);
            toggle.setAttribute("aria-expanded", open ? "true" : "false");
        }
        toggle.addEventListener("click", function () { setOpen(!panel.classList.contains("is-open")); });
        if (nMin && nMax && (nMin.value || nMax.value)) setOpen(true);
    }

    /* Enter in a price field submits the form (they use form="filter-form") */
})();
