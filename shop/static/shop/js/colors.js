/* Admin: when 4 colours are ticked, the others are disabled (the server checks it too). */
(function () {
    "use strict";
    var MAX = 4;
    var box = document.getElementById("id_colors");
    if (!box) return;
    var boxes = box.querySelectorAll('input[type="checkbox"]');

    function update() {
        var count = 0;
        boxes.forEach(function (b) { if (b.checked) count++; });
        boxes.forEach(function (b) { b.disabled = count >= MAX && !b.checked; });
    }
    boxes.forEach(function (b) { b.addEventListener("change", update); });
    update();
})();