/* Gallery on the details pages: images AND videos, with a slide animation.
   Save as:  shop/static/shop/js/gallery_media.js

   Arrow / thumbnail / key / swipe -> the current image or video slides out and
   the next one slides in. It replaces the old gallery code of product_details.js
   only for the gallery (zoom, copy link, etc. stay the same). */
(() => {
  "use strict";

  const box = document.getElementById("pd-thumbs");
  const stage = document.querySelector(".pd-stage");
  const frame = document.getElementById("pd-zoom-open");
  const mainImg = document.getElementById("pd-main-img");
  if (!box || !stage || !frame || !mainImg) return;

  const thumbs = Array.from(box.querySelectorAll(".pd-thumb"));
  if (thumbs.length < 2) return;                     // a single image: nothing to slide

  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  const OUT = 170, IN = 230;                         // milliseconds

  let index = Math.max(0, thumbs.findIndex((t) => t.classList.contains("is-active")));
  let player = null;
  let busy = false;

  const current = () => (player || frame);

  function swapContent(thumb) {
    if (player) { player.pause(); player.remove(); player = null; }
    if (thumb.dataset.video) {
      frame.hidden = true;
      player = document.createElement("video");
      player.className = "pd-stage-video";
      player.controls = true;
      player.playsInline = true;
      player.preload = "metadata";
      player.src = thumb.dataset.video + "#t=0.1";
      player.setAttribute("aria-label", thumb.dataset.alt || "");
      frame.after(player);
    } else {
      frame.hidden = false;
      mainImg.src = thumb.dataset.src;
      mainImg.alt = thumb.dataset.alt || "";
    }
  }

  async function show(i, dir) {
    const next = (i + thumbs.length) % thumbs.length;
    if (next === index || busy) return;
    busy = true;
    const way = dir || (next > index ? 1 : -1);       // 1: new one comes from the right
    index = next;
    thumbs.forEach((t, n) => t.classList.toggle("is-active", n === index));
    const thumb = thumbs[index];

    const left = thumb.offsetLeft - (box.clientWidth - thumb.offsetWidth) / 2;
    box.scrollTo({ left, behavior: reduced.matches ? "auto" : "smooth" });

    if (reduced.matches || !current().animate) {
      swapContent(thumb);
      busy = false;
      return;
    }

    try {
      if (player) player.pause();
      await current().animate(
        [{ transform: "translateX(0)", opacity: 1 },
         { transform: `translateX(${-way * 35}%)`, opacity: 0 }],
        { duration: OUT, easing: "ease-in", fill: "forwards" }
      ).finished;
      current().getAnimations().forEach((a) => a.cancel());
      swapContent(thumb);
      await current().animate(
        [{ transform: `translateX(${way * 35}%)`, opacity: 0 },
         { transform: "translateX(0)", opacity: 1 }],
        { duration: IN, easing: "ease-out" }
      ).finished;
    } catch (_) {
      swapContent(thumb);
    }
    busy = false;
  }

  // capture phase: we run before the old gallery code and stop it
  document.addEventListener("click", (e) => {
    const thumb = e.target.closest(".pd-thumb");
    if (thumb && box.contains(thumb)) {
      e.stopPropagation();
      show(thumbs.indexOf(thumb));
    } else if (e.target.closest("#pd-prev")) {
      e.stopPropagation();
      show(index - 1, -1);
    } else if (e.target.closest("#pd-next")) {
      e.stopPropagation();
      show(index + 1, 1);
    }
  }, true);

  document.addEventListener("keydown", (e) => {
    if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
    if (e.target.closest("input, textarea, select, video, [contenteditable]")) return;
    if (document.getElementById("pd-zoom")?.open) return;
    e.stopImmediatePropagation();
    const rtl = getComputedStyle(document.documentElement).direction === "rtl";
    const step = (e.key === "ArrowRight") !== rtl ? 1 : -1;
    show(index + step, step);
  }, true);

  // swipe on the phone
  let startX = 0, startY = 0;
  stage.addEventListener("touchstart", (e) => {
    startX = e.touches[0].clientX; startY = e.touches[0].clientY;
  }, { passive: true });
  stage.addEventListener("touchend", (e) => {
    if (e.target.closest("video")) return;           // do not fight the video controls
    const dx = e.changedTouches[0].clientX - startX;
    const dy = e.changedTouches[0].clientY - startY;
    if (Math.abs(dx) < 50 || Math.abs(dx) < Math.abs(dy) * 1.5) return;
    show(index + (dx < 0 ? 1 : -1), dx < 0 ? 1 : -1);
  }, { passive: true });
})();