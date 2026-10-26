
document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.querySelector(".nav-toggle");
    const nav = document.querySelector("#site-nav");

    if (!toggle || !nav) {
        return;
    }

    function closeMenu() {
        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-label", "Open menu");
        nav.classList.remove("is-open");
    }

    toggle.addEventListener("click", () => {
        const isOpen =
            toggle.getAttribute("aria-expanded") === "true";

        toggle.setAttribute("aria-expanded", String(!isOpen));
        toggle.setAttribute(
            "aria-label",
            isOpen ? "Open menu" : "Close menu"
        );

        nav.classList.toggle("is-open", !isOpen);
    });

    nav.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", closeMenu);
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeMenu();
        }
    });

    document.addEventListener("click", (event) => {
        if (
            !toggle.contains(event.target) &&
            !nav.contains(event.target)
        ) {
            closeMenu();
        }
    });

    window.addEventListener("resize", () => {
        if (window.innerWidth > 900) {
            closeMenu();
        }
    });
});
