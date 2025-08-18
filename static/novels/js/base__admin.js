$(document).ready(function () {
  const path = window.location.pathname;
  $('#sidebar .nav-link').each(function () {
    const linkPath = $(this).attr('href');
    if (linkPath === path) {
      $(this).addClass('active');
    } else {
      $(this).removeClass('active');
    }
  });
});

