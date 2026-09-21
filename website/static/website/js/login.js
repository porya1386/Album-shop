 var card = document.getElementById("auth-card");
    var overlay = document.getElementById("overlay");
    var paneLogin = document.getElementById("pane-login");
    var paneRegister = document.getElementById("pane-register");
    var ovLogin = document.getElementById("ov-login");
    var ovRegister = document.getElementById("ov-register");

    var TITLES = { login: "Log in | Your Name", register: "Register | Your Name" };

    // Show one of the two pages. Only the visible one can be reached with the keyboard.
    function setMode(mode, moveFocus) {
      card.setAttribute("data-mode", mode);
      document.title = TITLES[mode];

      var isLogin = mode === "login";
      paneLogin.inert = !isLogin;
      paneRegister.inert = isLogin;
      ovRegister.inert = !isLogin;
      ovLogin.inert = isLogin;
      paneLogin.setAttribute("aria-hidden", String(!isLogin));
      paneRegister.setAttribute("aria-hidden", String(isLogin));
      ovRegister.setAttribute("aria-hidden", String(!isLogin));
      ovLogin.setAttribute("aria-hidden", String(isLogin));

      if (moveFocus) {
        var first = (isLogin ? paneLogin : paneRegister).querySelector("input");
        if (first) first.focus({ preventScroll: true });
      }
    }

    // Keep the address bar in sync (/login/ <-> /register/, or #login / #register)
    function updateUrl(mode) {
      try {
        if (/\/(login|register)\/?$/.test(location.pathname)) {
          history.replaceState(null, "", location.pathname.replace(/(login|register)\/?$/, mode + "/"));
        } else {
          history.replaceState(null, "", "#" + mode);
        }
      } catch (e) { /* not important */ }
    }

    function switchTo(mode) {
      setMode(mode, true);
      updateUrl(mode);
    }

    // Click anywhere on the sliding panel (or its button) to switch
    overlay.addEventListener("click", function () {
      switchTo(card.getAttribute("data-mode") === "login" ? "register" : "login");
    });

    // Text links used on phones
    var switches = document.querySelectorAll("[data-switch]");
    for (var i = 0; i < switches.length; i++) {
      switches[i].addEventListener("click", function () {
        switchTo(this.getAttribute("data-switch"));
      });
    }

    // Which page to show first
    var start = document.body.getAttribute("data-start");
    if (!start) {
      start = (/register/.test(location.pathname) || location.hash === "#register") ? "register" : "login";
    }
    setMode(start, false);

    // Show / hide password buttons
    var pwButtons = document.querySelectorAll(".pw-toggle");
    for (var j = 0; j < pwButtons.length; j++) {
      pwButtons[j].addEventListener("click", function () {
        var input = document.getElementById(this.getAttribute("aria-controls"));
        var show = input.type === "password";
        input.type = show ? "text" : "password";
        this.textContent = show ? "Hide" : "Show";
        this.setAttribute("aria-pressed", String(show));
      });
    }

    // Both passwords must match
    var pass1 = document.getElementById("reg-password1");
    var pass2 = document.getElementById("reg-password2");
    function checkMatch() {
      pass2.setCustomValidity(pass2.value && pass1.value !== pass2.value ? "The two passwords do not match." : "");
    }
    pass1.addEventListener("input", checkMatch);
    pass2.addEventListener("input", checkMatch);

    // Mobile menu
    var toggle = document.querySelector(".nav-toggle");
    var nav = document.getElementById("site-nav");

    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-label", "Open menu");
        toggle.focus();
      }
    });

    // Current year in the footer
    document.getElementById("year").textContent = new Date().getFullYear();