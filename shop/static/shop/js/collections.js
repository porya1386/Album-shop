/* Slide animation when you switch between Paintings and Sculptures.
   Save as:  shop/static/shop/js/collections.js

   The tab you click is on the RIGHT of the current one  -> the list slides out to the left and the new one
   comes in from the right. Tab on the LEFT -> the opposite. (It follows the real position of the tabs, so
   it is also correct in Farsi/RTL.)  The page is still a normal page load: search, likes, links keep working. */
(() => {
  "use strict";

  const OUT_MS = 320;                       // the pill slides this long (CSS .collection-pill), then the page opens
  // false: only the highlight on the tabs slides (the list just appears)
  const SLIDE_LIST = true;
  // On phones and tablets the list does not slide: moving a wide element sideways makes the mobile
  // browser zoom out / re-layout the page. (The highlight on the tabs still slides everywhere.)
  const smallScreen = window.matchMedia("(max-width: 900px), (pointer: coarse)");
  // false: follow the real position of the tabs (in Farsi/RTL the direction is mirrored, like the tabs)
  // true : always Paintings -> Sculptures = right to left, Sculptures -> Paintings = left to right
  const SAME_DIRECTION_IN_RTL = false;
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");

  const results = document.querySelector(".results");
  const nav = document.querySelector(".collection-tabs");
  const tabs = document.querySelectorAll(".collection-tab");
  const root = document.documentElement;

  /* ---- the highlight (pill) that slides between the two tabs ---- */
  const initialActive = nav && nav.querySelector(".collection-tab.is-active");
  let pill = null;

  function placePill(tab) {
    if (!pill || !tab) return;
    pill.style.setProperty("--x", `${tab.offsetLeft}px`);
    pill.style.setProperty("--w", `${tab.offsetWidth}px`);
  }

  if (nav && initialActive) {
    pill = document.createElement("span");
    pill.className = "collection-pill";
    pill.setAttribute("aria-hidden", "true");
    nav.prepend(pill);
    placePill(initialActive);
    nav.classList.add("has-pill");
    // switch the transition on only after the first position, so it does not slide on page load
    requestAnimationFrame(() => requestAnimationFrame(() => nav.classList.add("is-ready")));

    const refit = () => placePill(nav.querySelector(".collection-tab.is-active"));
    if ("ResizeObserver" in window) new ResizeObserver(refit).observe(nav);
    window.addEventListener("load", refit);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(refit);
  }

  /* the page we arrived on: let the head script's "slide in" finish, then clean up */
  if (root.hasAttribute("data-slide")) {
    const done = () => root.removeAttribute("data-slide");
    if (results) results.addEventListener("animationend", done, { once: true });
    setTimeout(done, 900);                  // safety net
  }

  /* back button (bfcache) must not show a half-hidden list */
  window.addEventListener("pageshow", (event) => {
    if (!event.persisted) return;
    if (results) results.classList.remove("is-leaving-left", "is-leaving-right");
    root.removeAttribute("data-slide");
    if (initialActive) {
      tabs.forEach((t) => t.classList.toggle("is-active", t === initialActive));
      placePill(initialActive);
    }
  });

  if (!results || !tabs.length) return;

  tabs.forEach((tab) => {
  tab.addEventListener("click", async (event) => {
    if (event.defaultPrevented || event.button !== 0) return;
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    if (tab.classList.contains("is-active") || reduced.matches) return;

    event.preventDefault();

    const current = nav.querySelector(".collection-tab.is-active");
    if (!current) return;

    const toRight =
      tab.getBoundingClientRect().left >
      current.getBoundingClientRect().left;

    // Move the active tab highlight
    current.classList.remove("is-active");
    tab.classList.add("is-active");
    placePill(tab);

    // Animate old products out
    const slideList = SLIDE_LIST && !smallScreen.matches;

    if (slideList) {
      results.classList.add(
        toRight ? "is-leaving-left" : "is-leaving-right"
      );
    }

    try {
      // Wait for exit animation
      await new Promise(resolve => setTimeout(resolve, OUT_MS));

      const response = await fetch(tab.href, {
        method: "GET",
        headers: {
          "X-Requested-With": "XMLHttpRequest"
        },
        credentials: "same-origin"
      });

      if (!response.ok) {
        throw new Error("Could not load collection");
      }

      const html = await response.text();

      // Parse returned HTML
      const parser = new DOMParser();
      const newDocument = parser.parseFromString(html, "text/html");
      const newResults = newDocument.querySelector(".results");

      if (!newResults) {
        throw new Error("Results element not found");
      }

      // Replace only product results
      results.innerHTML = newResults.innerHTML;

      // Update browser URL without reloading
      history.pushState({}, "", tab.href);

      // Remove old animation classes
      results.classList.remove(
        "is-leaving-left",
        "is-leaving-right"
      );

      // Update active tab
      tabs.forEach(t => {
        t.classList.toggle("is-active", t.href === tab.href);
      });

      placePill(tab);

    } catch (error) {
      console.error(error);

      // Fallback if fetch fails
      window.location.href = tab.href;
    }
  });
});
})();