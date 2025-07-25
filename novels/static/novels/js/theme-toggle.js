$(function () {
  const $html = $('html');
  const $btn = $('#toggleThemeBtn');

  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    $html.attr('data-bs-theme', savedTheme);
    updateButtonText(savedTheme);
  }

  $btn.on('click', function (event) {
    event.stopPropagation();
    const currentTheme = $html.attr('data-bs-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    $html.attr('data-bs-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateButtonText(newTheme);
  });

  function updateButtonText(theme) {
    if (theme === 'dark') {
      $btn.html("<i class='bxr bx-sun-bright'></i> Light");
    } else {
      $btn.html("<i class='bxr bx-moon-star'></i> Dark");
    }
  }
});
