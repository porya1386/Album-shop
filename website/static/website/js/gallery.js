/* Home page marquees (paintings + sculptures).
   Save as:  website/static/website/js/gallery.js   (replaces the old file)

   Works for EVERY  .marquee  on the page: it clones the list until the track is
   long enough, then sets --shift (width of one list) and --dur (speed) for the CSS animation. */
(() => {
  "use strict";

  const SPEED = 65;                 // pixels per second (bigger = faster)
  const MIN_DURATION = 14;          // seconds, so a short list is never too fast
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");

  function build(marquee) {
    const viewport = marquee.querySelector(".marquee-viewport");
    const track = marquee.querySelector(".marquee-track");
    const group = marquee.querySelector(".marquee-group");
    if (!viewport || !track || !group) return;

    // remove the clones from a previous run (resize)
    track.querySelectorAll("[data-clone]").forEach((node) => node.remove());

    const groupWidth = group.getBoundingClientRect().width;
    const viewWidth = viewport.clientWidth;
    if (!groupWidth || !viewWidth) return;

    // user prefers no motion: no clones, no animation, the row can be scrolled by hand
    if (reduced.matches) {
      track.style.animation = "none";
      viewport.style.overflowX = "auto";
      return;
    }
    track.style.animation = "";
    viewport.style.overflowX = "";

    // one list + enough copies to always cover the viewport while it moves by one list
    const copies = Math.ceil(viewWidth / groupWidth);
    for (let i = 0; i < copies; i += 1) {
      const clone = group.cloneNode(true);
      clone.removeAttribute("id");
      clone.setAttribute("aria-hidden", "true");
      clone.setAttribute("data-clone", "");
      clone.querySelectorAll("a").forEach((a) => a.setAttribute("tabindex", "-1"));
      track.appendChild(clone);
    }

    track.style.setProperty("--shift", `${groupWidth}px`);
    track.style.setProperty("--dur", `${Math.max(MIN_DURATION, groupWidth / SPEED)}s`);
  }

  function init() {
    const marquees = document.querySelectorAll(".marquee");

    marquees.forEach((marquee) => {
      build(marquee);

      // rebuild when the width changes (rotate phone, resize window)
      let lastWidth = marquee.clientWidth;
      let timer = 0;
      if ("ResizeObserver" in window) {
        new ResizeObserver(() => {
          if (marquee.clientWidth === lastWidth) return;
          lastWidth = marquee.clientWidth;
          clearTimeout(timer);
          timer = setTimeout(() => build(marquee), 150);
        }).observe(marquee);
      }

      // do not animate while it is off screen
      if ("IntersectionObserver" in window) {
        const track = marquee.querySelector(".marquee-track");
        new IntersectionObserver((entries) => {
          entries.forEach((entry) => {
            track.style.animationPlayState = entry.isIntersecting ? "" : "paused";
          });
        }).observe(marquee);
      }
    });

    reduced.addEventListener?.("change", () => marquees.forEach(build));
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
  // images/fonts can change nothing in the width, but a late load is a cheap safety net
  window.addEventListener("load", () => document.querySelectorAll(".marquee").forEach(build));
})();