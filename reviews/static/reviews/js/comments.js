/* Add and delete comments without reloading the page.
   Save as:  reviews/static/reviews/js/comments.js

   Without JavaScript (or if something fails) the forms still work the normal way. */
(() => {
  "use strict";

  const section = document.getElementById("comments");
  if (!section || !window.fetch || !window.FormData) return;

  const countEl = section.querySelector(".cm-count");
  const GENERIC_ERROR = section.dataset.error || "Something went wrong. Please try again.";

  const setCount = (n) => { if (countEl) countEl.textContent = n; };

  function ensureList() {
    let list = section.querySelector(".cm-list");
    if (!list) {
      list = document.createElement("ul");
      list.className = "cm-list";
      const empty = section.querySelector(".cm-empty");
      if (empty) empty.replaceWith(list); else section.appendChild(list);
    }
    return list;
  }

  function showError(form, message) {
    let box = form.querySelector(".cm-error");
    if (!message) { if (box) box.remove(); return; }
    if (!box) {
      box = document.createElement("p");
      box.className = "cm-error";
      box.setAttribute("role", "alert");
      form.insertBefore(box, form.querySelector("label") || form.firstChild);
    }
    box.textContent = message;
  }

  async function post(form) {
    const res = await fetch(form.action, {
      method: "POST",
      body: new FormData(form),
      credentials: "same-origin",
      headers: { "X-Requested-With": "XMLHttpRequest", "Accept": "application/json" },
    });
    // logged out -> Django redirected us to the login page: go there like a normal click
    if (res.redirected && !(res.headers.get("content-type") || "").includes("json")) {
      window.location.href = res.url;
      return null;
    }
    return res.json();
  }

  async function addComment(form) {
    const field = form.querySelector("textarea");
    const button = form.querySelector('button[type="submit"]');
    if (!field || !field.value.trim()) { field && field.focus(); return; }

    button.disabled = true;
    try {
      const data = await post(form);
      if (!data) return;
      if (!data.ok) { showError(form, data.error || GENERIC_ERROR); return; }

      showError(form, "");
      const list = ensureList();
      list.insertAdjacentHTML("afterbegin", data.html);
      list.firstElementChild.classList.add("is-new");
      setCount(data.count);

      field.value = "";
      field.dispatchEvent(new Event("input", { bubbles: true }));
      field.focus({ preventScroll: true });
    } catch (err) {
      showError(form, GENERIC_ERROR);
    } finally {
      button.disabled = false;
    }
  }

  async function deleteComment(form) {
    const item = form.closest(".cm-item");
    const button = form.querySelector("button");
    if (button) button.disabled = true;
    try {
      const data = await post(form);
      if (!data) return;
      if (!data.ok) { if (button) button.disabled = false; return; }

      item.classList.add("is-removing");
      setTimeout(() => {
        const list = item.parentElement;
        item.remove();
        setCount(data.count);
        if (list && !list.children.length) {
          const empty = document.createElement("p");
          empty.className = "cm-empty";
          empty.textContent = section.dataset.empty || "";
          list.replaceWith(empty);
        }
      }, 200);
    } catch (err) {
      if (button) button.disabled = false;
    }
  }

  section.addEventListener("submit", (event) => {
    // the delete form asks "are you sure?" first; if the user said no, do nothing
    if (event.defaultPrevented) return;
    const form = event.target;
    if (form.matches(".cm-form")) {
      event.preventDefault();
      addComment(form);
    } else if (form.matches(".cm-delete")) {
      event.preventDefault();
      deleteComment(form);
    }
  });
})();