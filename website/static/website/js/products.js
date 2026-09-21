    /*
      ------------------------------------------------------------
      YOUR PRODUCTS
      Edit this list to add, remove or change paintings.
      All titles, sizes, years, prices and descriptions below are placeholders.
      To use your own image, put its path or URL in "image".
      ------------------------------------------------------------
    */
    var WIKI = "https://commons.wikimedia.org/wiki/Special:FilePath/";
    var DESC = "Write a few lines about this painting here: what inspired it, how long it took, and what makes it special to you.";

    var PRODUCTS = [
      { title: "Sunrise on Mount Tacoma", price: "$450", medium: "Oil on canvas", size: "60 x 90 cm", year: "2026",
        image: WIKI + "Albert_Bierstadt_-_Sunrise_on_Mount_Tacoma.jpg", description: DESC },
      { title: "Snow in the Rockies", price: "$520", medium: "Oil on canvas", size: "70 x 100 cm", year: "2026",
        image: WIKI + "Albert_Bierstadt_-_Snow_in_the_Rockies.jpg", description: DESC },
      { title: "Mountain House", price: "$380", medium: "Oil on canvas", size: "50 x 70 cm", year: "2025",
        image: WIKI + "Albert_Bierstadt_-_Mountain_House.jpg", description: DESC },
      { title: "In the Mountains", price: "$410", medium: "Oil on board", size: "50 x 70 cm", year: "2025",
        image: WIKI + "Bierstadt_Albert_In_the_Mountains.jpg", description: DESC },
      { title: "By a Mountain Lake", price: "$350", medium: "Oil on canvas", size: "40 x 60 cm", year: "2025",
        image: WIKI + "Bierstadt_Albert_By_a_Mountain_Lake.jpg", description: DESC },
      { title: "Sacramento River Valley", price: "$480", medium: "Oil on canvas", size: "60 x 100 cm", year: "2024",
        image: WIKI + "Bierstadt_Albert_Sacramento_River_Valley.jpg", description: DESC }
    ];

    // Build the product grid
    var grid = document.getElementById("grid");

    PRODUCTS.forEach(function (p, i) {
      var figure = document.createElement("figure");
      figure.className = "product";

      var frame = document.createElement("div");
      frame.className = "frame";
      var img = document.createElement("img");
      img.src = p.image + "?width=800";
      img.alt = p.title + " (painting)";
      img.loading = "lazy";
      frame.appendChild(img);

      var info = document.createElement("figcaption");
      info.className = "product-info";

      var h2 = document.createElement("h2");
      h2.textContent = p.title;

      var meta = document.createElement("p");
      meta.className = "meta";
      meta.textContent = p.medium + ", " + p.size;

      var foot = document.createElement("div");
      foot.className = "product-foot";

      var price = document.createElement("span");
      price.className = "price";
      price.textContent = p.price;

      var button = document.createElement("button");
      button.type = "button";
      button.className = "btn btn-ghost";
      button.textContent = "About this painting";
      button.addEventListener("click", function () { openDetails(i); });

      foot.appendChild(price);
      foot.appendChild(button);
      info.appendChild(h2);
      info.appendChild(meta);
      info.appendChild(foot);
      figure.appendChild(frame);
      figure.appendChild(info);
      grid.appendChild(figure);
    });

    // Details window
    var dialog = document.getElementById("details");

    function openDetails(index) {
      var p = PRODUCTS[index];
      var image = document.getElementById("d-image");
      image.src = p.image + "?width=1400";
      image.alt = p.title + " (painting)";
      document.getElementById("d-title").textContent = p.title;
      document.getElementById("d-price").textContent = p.price;
      document.getElementById("d-desc").textContent = p.description;
      document.getElementById("d-medium").textContent = p.medium;
      document.getElementById("d-size").textContent = p.size;
      document.getElementById("d-year").textContent = p.year;
      document.getElementById("d-buy").href =
        "mailto:you@example.com?subject=" + encodeURIComponent("Question about: " + p.title);
      dialog.showModal();
    }

    document.getElementById("d-close").addEventListener("click", function () { dialog.close(); });

    // Clicking the dark area outside the window closes it
    dialog.addEventListener("click", function (e) {
      if (e.target === dialog) dialog.close();
    });

    // Mobile menu
    var toggle = document.querySelector(".nav-toggle");
    var nav = document.getElementById("site-nav");

    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open);
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