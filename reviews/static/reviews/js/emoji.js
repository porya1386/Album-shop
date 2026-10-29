/* Emoji picker for the comment box. No libraries.
   Markup: <form data-emoji-form> ... <textarea> ... <button data-emoji-toggle> <div data-emoji-panel>
   Names of the tabs come from data-t-* attributes (the template translates them). */
(function () {
    "use strict";

    var form = document.querySelector("[data-emoji-form]");
    if (!form) return;
    var textarea = form.querySelector("textarea");
    var toggle = form.querySelector("[data-emoji-toggle]");
    var panel = form.querySelector("[data-emoji-panel]");
    if (!textarea || !toggle || !panel) return;

    var T = form.dataset;
    var CATEGORIES = [
        { id: "recent",   icon: "🕘", name: T.tRecent   || "Recent",   list: [] },
        { id: "smileys",  icon: "😀", name: T.tSmileys  || "Smileys",  list: "😀 😃 😄 😁 😆 😅 😂 🤣 😊 😇 🙂 🙃 😉 😌 😍 🥰 😘 😗 😋 😛 😜 🤪 😎 🤩 🥳 😏 😒 😞 😔 😢 😭 😤 😡 🤯 😱 😨 😴 🤔 🤗 🤭 🙄 😬 🥺 😳".split(" ") },
        { id: "gestures", icon: "👍", name: T.tGestures || "Gestures", list: "👍 👎 👏 🙌 👐 🤝 🙏 💪 👌 ✌️ 🤞 🤟 🤘 👋 🤚 ✋ 👈 👉 👆 👇 ☝️ ✊ 👊 🤛 🤜 🫶".split(" ") },
        { id: "hearts",   icon: "❤️", name: T.tHearts   || "Hearts",   list: "❤️ 🧡 💛 💚 💙 💜 🖤 🤍 🤎 💔 ❣️ 💕 💞 💓 💗 💖 💘 💝 ✨ 🌟 ⭐ 💫 🔥 💯 🎉 🎊".split(" ") },
        { id: "art",      icon: "🎨", name: T.tArt      || "Art",      list: "🎨 🖼️ 🖌️ 🖍️ 📷 🎭 🎬 🎵 🎶 📚 ✏️ 💡 🏆 🥇 🎁 💎 👑 🔔 📌 🛍️ 🛒 💰".split(" ") },
        { id: "nature",   icon: "🌸", name: T.tNature   || "Nature",   list: "🌸 🌹 🌺 🌻 🌷 🌼 🍀 🌿 🌲 🌳 🍁 🍂 🌈 ☀️ 🌙 ⛅ ☁️ 🌊 🏔️ 🌄 🌅 🦋 🐦 🐱 🐶".split(" ") },
        { id: "food",     icon: "☕",       name: T.tFood     || "Food",     list: "☕ 🍵 🍰 🍪 🍫 🍎 🍓 🍒 🍇 🍉 🍕 🍔 🥐 🍷 🥂 🍾".split(" ") }
    ];

    var RECENT_KEY = "jahan-emoji-recent";
    var MAX_RECENT = 16;
    var current = "smileys";

    function loadRecent() {
        try {
            var v = JSON.parse(localStorage.getItem(RECENT_KEY) || "[]");
            return Array.isArray(v) ? v.slice(0, MAX_RECENT) : [];
        } catch (e) { return []; }
    }
    function saveRecent(emoji) {
        var list = loadRecent().filter(function (x) { return x !== emoji; });
        list.unshift(emoji);
        try { localStorage.setItem(RECENT_KEY, JSON.stringify(list.slice(0, MAX_RECENT))); } catch (e) { /* ignore */ }
    }

    /* ---- build the panel ---- */
    var tabs = document.createElement("div");
    tabs.className = "cm-emoji-tabs";
    tabs.setAttribute("role", "tablist");
    var grid = document.createElement("div");
    grid.className = "cm-emoji-grid";
    grid.id = "cm-emoji-grid";
    panel.appendChild(tabs);
    panel.appendChild(grid);

    CATEGORIES.forEach(function (cat) {
        var b = document.createElement("button");
        b.type = "button";
        b.className = "cm-emoji-tab";
        b.setAttribute("role", "tab");
        b.setAttribute("aria-controls", "cm-emoji-grid");
        b.setAttribute("aria-label", cat.name);
        b.title = cat.name;
        b.dataset.cat = cat.id;
        b.textContent = cat.icon;
        b.addEventListener("click", function () { show(cat.id); });
        tabs.appendChild(b);
    });

    function show(id) {
        current = id;
        var cat = CATEGORIES.filter(function (c) { return c.id === id; })[0];
        var list = id === "recent" ? loadRecent() : cat.list;
        Array.prototype.forEach.call(tabs.children, function (t) {
            t.setAttribute("aria-selected", t.dataset.cat === id ? "true" : "false");
        });
        grid.textContent = "";
        if (!list.length) {
            var empty = document.createElement("p");
            empty.className = "cm-emoji-empty";
            empty.textContent = "—";
            grid.appendChild(empty);
            return;
        }
        list.forEach(function (emoji) {
            var b = document.createElement("button");
            b.type = "button";
            b.className = "cm-emoji-item";
            b.textContent = emoji;
            b.setAttribute("aria-label", emoji);
            b.addEventListener("click", function () { insert(emoji); });
            grid.appendChild(b);
        });
    }

    /* ---- put the emoji where the cursor is ---- */
    function insert(emoji) {
        var max = parseInt(textarea.getAttribute("maxlength"), 10) || Infinity;
        var start = textarea.selectionStart, end = textarea.selectionEnd;
        if (typeof start !== "number") { start = end = textarea.value.length; }
        var next = textarea.value.length - (end - start) + emoji.length;
        if (next > max) return;                          // the box is full
        textarea.focus();
        textarea.setRangeText(emoji, start, end, "end");
        textarea.dispatchEvent(new Event("input", { bubbles: true }));
        saveRecent(emoji);
    }

    /* ---- open / close ---- */
    function open() {
        if (loadRecent().length && current === "smileys" && !panel.dataset.opened) current = "recent";
        panel.dataset.opened = "1";
        show(current);
        panel.hidden = false;
        toggle.setAttribute("aria-expanded", "true");
    }
    function close(returnFocus) {
        panel.hidden = true;
        toggle.setAttribute("aria-expanded", "false");
        if (returnFocus) toggle.focus();
    }

    toggle.hidden = false;                               // without JavaScript the button stays hidden
    toggle.addEventListener("click", function () {
        if (panel.hidden) open(); else close(false);
    });
    document.addEventListener("click", function (e) {
        if (!panel.hidden && !panel.contains(e.target) && !toggle.contains(e.target)) close(false);
    });
    form.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && !panel.hidden) { e.preventDefault(); close(true); }
    });
})();