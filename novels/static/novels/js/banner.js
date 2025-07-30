let index = 0;
  const banner = document.getElementById('slideshow-banner');

  setInterval(() => {
    index = (index + 1) % images.length;
    banner.src = images[index];
  }, 5000); 
