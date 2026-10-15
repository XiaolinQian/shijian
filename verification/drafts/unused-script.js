(function(){
  const links = document.querySelectorAll('a[href^="#"]');
  links.forEach(link => link.addEventListener('click', event => {
    const target = document.querySelector(link.getAttribute('href'));
    if (target) { event.preventDefault(); target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  }));
  document.querySelectorAll('a[download]').forEach(link => {
    link.addEventListener('click', () => { link.classList.add('is-downloading'); window.setTimeout(() => link.classList.remove('is-downloading'), 900); });
  });
})();
