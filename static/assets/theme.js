(() => {
  const html = document.documentElement;
  html.classList.add('js');
  try {
    if (localStorage.getItem('hw-editorial-theme') === 'light') html.dataset.theme = 'light';
  } catch (_) {}
})();
