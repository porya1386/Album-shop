(function () {
    "use strict";

    const dialog = document.getElementById("details");
    if (!dialog) return;

    const els = {
        image: document.getElementById("d-image"),
        title: document.getElementById("d-title"),
        price: document.getElementById("d-price"),
        desc: document.getElementById("d-desc"),
        size: document.getElementById("d-size"),
        year: document.getElementById("d-year"),
        buy: document.getElementById("d-buy"),
        page: document.getElementById("d-page"),
        close: document.getElementById("d-close"),
    };

    function openDetails(button) {
        const d = button.dataset;

        els.image.src = d.image;
        els.image.alt = d.title;
        els.title.textContent = d.title;
        els.price.textContent = d.price;
        els.desc.textContent = d.description;
        els.size.textContent = d.size;
        els.year.textContent = d.year;

        // "Ask about" button: hide it if the painting is sold
        const sold = d.sold === "true";
        els.buy.hidden = sold;
        els.buy.href = "mailto:?subject=" + encodeURIComponent("Question about: " + d.title);

        // Link to the product's own slug page (built by Django)
        els.page.href = d.url || "#";

        if (typeof dialog.showModal === "function") {
            dialog.showModal();
        } else {
            dialog.setAttribute("open", "");
        }
    }

    function closeDetails() {
        if (typeof dialog.close === "function") {
            dialog.close();
        } else {
            dialog.removeAttribute("open");
        }
    }

    // Event delegation: works for every card rendered by Django
    document.getElementById("grid").addEventListener("click", function (e) {
        const button = e.target.closest(".js-open-details");
        if (button) openDetails(button);
    });

    els.close.addEventListener("click", closeDetails);

    // Click on the dark backdrop closes the dialog
    dialog.addEventListener("click", function (e) {
        if (e.target === dialog) closeDetails();
    });
})();
