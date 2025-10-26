(function ($) {
    "use strict";
    
    // Dropdown on mouse hover
    $(document).ready(function () {
        function toggleNavbarMethod() {
            if ($(window).width() > 992) {
                $('.navbar .dropdown').on('mouseover', function () {
                    $('.dropdown-toggle', this).trigger('click');
                }).on('mouseout', function () {
                    $('.dropdown-toggle', this).trigger('click').blur();
                });
            } else {
                $('.navbar .dropdown').off('mouseover').off('mouseout');
            }
        }
        toggleNavbarMethod();
        $(window).resize(toggleNavbarMethod);
    });
    
    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 100) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });
    $('.back-to-top').click(function () {
        $('html, body').animate({scrollTop: 0}, 1500, 'easeInOutExpo');
        return false;
    });

    // Carousels
    $(".tranding-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 2000,
        items: 1,
        dots: false,
        loop: true,
        nav : true,
        navText : ['<i class="fa fa-angle-left"></i>', '<i class="fa fa-angle-right"></i>']
    });

    $(".carousel-item-1").owlCarousel({
        autoplay: true,
        smartSpeed: 1500,
        items: 1,
        dots: false,
        loop: true,
        nav : true,
        navText : ['<i class="fa fa-angle-left" aria-hidden="true"></i>', '<i class="fa fa-angle-right" aria-hidden="true"></i>']
    });

    $(".carousel-item-2").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        margin: 30,
        dots: false,
        loop: true,
        nav : true,
        navText : ['<i class="fa fa-angle-left" aria-hidden="true"></i>', '<i class="fa fa-angle-right" aria-hidden="true"></i>'],
        responsive: { 0:{items:1}, 576:{items:1}, 768:{items:2} }
    });

    $(".carousel-item-3").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        margin: 30,
        dots: false,
        loop: true,
        nav : true,
        navText : ['<i class="fa fa-angle-left" aria-hidden="true"></i>', '<i class="fa fa-angle-right" aria-hidden="true"></i>'],
        responsive: { 0:{items:1}, 576:{items:1}, 768:{items:2}, 992:{items:3} }
    });

    $(".carousel-item-4").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        margin: 30,
        dots: false,
        loop: true,
        nav : true,
        navText : ['<i class="fa fa-angle-left" aria-hidden="true"></i>', '<i class="fa fa-angle-right" aria-hidden="true"></i>'],
        responsive: { 0:{items:1}, 576:{items:1}, 768:{items:2}, 992:{items:3}, 1200:{items:4} }
    });

})(jQuery);

// Template loader
async function loadTemplate(id, url) {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Failed to load ${url}`);
    const html = await res.text();
    document.getElementById(id).innerHTML = html;
  } catch (err) {
    console.error(err);
  }
}

// Load reusable templates dynamically
document.addEventListener('DOMContentLoaded', async () => {
  await loadTemplate('header', '/ScreamLine/templates/header.html');
  await loadTemplate('footer', '/ScreamLine/templates/footer.html');
  await loadTemplate('sidebar', '/ScreamLine/templates/sidebar.html');
  await loadTemplate('bottom-news', '/ScreamLine/templates/bottom-news.html');
  await loadTemplate('ad-banner', '/ScreamLine/templates/ad-banner.html');

  // Now header is loaded, so we can safely set date/time
  const dateElement = document.getElementById("current-date");
  if (dateElement) {
      const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
      function updateDateTime() {
          const now = new Date();
          dateElement.textContent = now.toLocaleDateString('en-US', options) + 
                                    " | " + now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      }
      updateDateTime();
      setInterval(updateDateTime, 1000);
  }
});
