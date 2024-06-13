jQuery(document).ready(function ($) {
  "use strict";

  // AOS initialization (commented out as it's not being used)
  // AOS.init({
  //   duration: 800,
  //   easing: "ease-in-out",
  //   once: true,
  // });

  // Function to remove loader
  var removeLoader = function () {
    setTimeout(function () {
      $("#loader").removeClass("show");
    }, 1);
  };
  removeLoader();

  // Function to clone navigation for mobile menu
  var siteMenuClone = function () {
    $(".js-clone-nav").each(function () {
      var $this = $(this);
      $this
        .clone()
        .attr("class", "site-nav-wrap")
        .appendTo(".site-mobile-menu-body");
    });

    setTimeout(function () {
      var counter = 0;
      $(".site-mobile-menu .has-children").each(function () {
        var $this = $(this);

        $this.prepend('<span class="arrow-collapse collapsed">');

        $this.find(".arrow-collapse").attr({
          "data-toggle": "collapse",
          "data-target": "#collapseItem" + counter,
        });

        $this.find("> ul").attr({
          class: "collapse",
          id: "collapseItem" + counter,
        });

        counter++;
      });
    }, 1000);

    $("body").on("click", ".arrow-collapse", function (e) {
      var $this = $(this);
      if ($this.closest("li").find(".collapse").hasClass("show")) {
        $this.removeClass("active");
      } else {
        $this.addClass("active");
      }
      e.preventDefault();
    });

    $(window).resize(function () {
      var $this = $(this),
        w = $this.width();

      if (w > 768) {
        if ($("body").hasClass("offcanvas-menu")) {
          $("body").removeClass("offcanvas-menu");
        }
      }
    });

    $("body").on("click", ".js-menu-toggle", function (e) {
      var $this = $(this);
      e.preventDefault();

      if ($("body").hasClass("offcanvas-menu")) {
        $("body").removeClass("offcanvas-menu");
        $this.removeClass("active");
      } else {
        $("body").addClass("offcanvas-menu");
        $this.addClass("active");
      }
    });

    // click outside offcanvas
    $(document).mouseup(function (e) {
      var container = $(".site-mobile-menu");
      if (!container.is(e.target) && container.has(e.target).length === 0) {
        if ($("body").hasClass("offcanvas-menu")) {
          $("body").removeClass("offcanvas-menu");
        }
      }
    });
  };
  siteMenuClone();

  // Function to handle sticky header
  var siteSticky = function () {
    if ($(".js-sticky-header").length) {
      $(".js-sticky-header").sticky({ topSpacing: 0 });
    }
  };
  siteSticky();

  // Hero slider
  if ($(".hero-slide").length) {
    $(".hero-slide").owlCarousel({
      items: 1,
      loop: true,
      autoplay: true,
      nav: true,
      dots: true,
      navText: [
        '<span class="icon-arrow_back">',
        '<span class="icon-arrow_forward">',
      ],
      smartSpeed: 1000,
    });
  }

  // Function to handle back-to-top button
  var backToTopButton = document.getElementById("back-to-top");

  if (backToTopButton) {
    window.onscroll = function () {
      if (
        document.body.scrollTop > 20 ||
        document.documentElement.scrollTop > 20
      ) {
        backToTopButton.style.display = "block";
      } else {
        backToTopButton.style.display = "none";
      }
    };

    backToTopButton.addEventListener("click", function (event) {
      event.preventDefault();
      document.body.scrollTop = 0;
      document.documentElement.scrollTop = 0;
    });
  }
});
