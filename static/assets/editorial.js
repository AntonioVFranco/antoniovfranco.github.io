(() => {
  'use strict';
  const root = document.documentElement;
  const params = new URLSearchParams(location.search);
  const picker = document.querySelector('.language');
  const choices = [...document.querySelectorAll('[data-lang-choice]')];
  const theme = document.querySelector('.theme-switch');

  function selectTheme(value) {
    root.dataset.theme = value;
    theme?.setAttribute('aria-pressed', String(value === 'light'));
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', value === 'light' ? '#ffffff' : '#000000');
  }
  selectTheme(root.dataset.theme);
  theme?.addEventListener('click', () => {
    const value = root.dataset.theme === 'light' ? 'dark' : 'light';
    try { localStorage.setItem('hw-editorial-theme', value); } catch (_) {}
    selectTheme(value);
  });
  window.addEventListener('storage', event => {
    if (event.key === 'hw-editorial-theme') selectTheme(event.newValue === 'light' ? 'light' : 'dark');
  });

  function saveLanguage(code) {
    try { localStorage.setItem('hw-language', code); } catch (_) {}
    if (location.protocol === 'https:') {
      document.cookie = 'hw-language=' + code + '; Max-Age=31536000; Path=/; SameSite=Lax; Secure';
    }
  }
  function targetFor(link) {
    const target = new URL(link.href);
    const query = new URLSearchParams(location.search);
    query.delete('lang');
    target.search = query.toString();
    target.hash = location.hash;
    return target;
  }
  let saved;
  try { saved = localStorage.getItem('hw-language'); } catch (_) {}
  if (document.body.hasAttribute('data-language-entry')) {
    const requested = choices.find(link => link.dataset.langChoice === params.get('lang'));
    const choice = requested || choices.find(link => link.dataset.langChoice === saved);
    if (choice && (choice.dataset.langChoice !== 'en' || requested)) {
      if (requested) saveLanguage(choice.dataset.langChoice);
      location.replace(targetFor(choice));
      return;
    }
  }
  for (const link of choices) {
    link.addEventListener('click', () => {
      saveLanguage(link.dataset.langChoice);
      link.href = targetFor(link);
    });
  }
  document.addEventListener('click', event => {
    if (picker?.open && !picker.contains(event.target)) picker.open = false;
  });
  document.addEventListener('keydown', event => {
    if (picker?.open && event.key === 'Escape') {
      picker.open = false;
      picker.querySelector('summary').focus();
    }
  });

  const search = document.querySelector('#article-search');
  if (search) {
    const buttons = [...document.querySelectorAll('[data-category-filter]')];
    const stories = [...document.querySelectorAll('[data-category]')];
    const normalize = text => text.normalize('NFKD').replace(/\p{M}/gu, '').toLowerCase();
    const filters = buttons.map(button => button.dataset.categoryFilter);
    let category = filters.includes(params.get('topic')) ? params.get('topic') : 'all';

    function applyFilters(syncUrl = false) {
      const query = normalize(search.value.trim());
      let visible = 0;
      for (const story of stories) {
        const matches = (category === 'all' || story.dataset.category === category) && normalize(story.textContent).includes(query);
        story.hidden = !matches;
        if (matches) visible += 1;
      }
      for (const button of buttons) button.setAttribute('aria-pressed', String(button.dataset.categoryFilter === category));
      document.querySelector('.empty-state').hidden = visible > 0;
      if (syncUrl && location.protocol !== 'file:') {
        const current = new URL(location.href);
        if (search.value.trim()) current.searchParams.set('search', search.value.trim());
        else current.searchParams.delete('search');
        if (category !== 'all') current.searchParams.set('topic', category);
        else current.searchParams.delete('topic');
        history.replaceState(null, '', current);
      }
    }
    search.value = params.get('search') || '';
    search.addEventListener('input', () => applyFilters(true));
    for (const button of buttons) {
      button.addEventListener('click', () => {
        category = button.dataset.categoryFilter;
        applyFilters(true);
      });
    }
    applyFilters();
  }

  const share = document.querySelector('[data-share-url]');
  if (share) {
    share.addEventListener('click', async () => {
      const url = share.dataset.shareUrl;
      try {
        await navigator.clipboard.writeText(url);
        share.querySelector('span').textContent = share.dataset.copied;
        document.querySelector('#share-status').textContent = share.dataset.copied;
      } catch (_) {
        let field = document.querySelector('.share-fallback');
        if (!field) {
          field = document.createElement('input');
          field.className = 'share-fallback';
          field.readOnly = true;
          field.value = url;
          field.setAttribute('aria-label', share.dataset.copyLabel);
          share.parentElement.append(field);
        }
        field.focus();
        field.select();
      }
    });
  }

  const toc = document.querySelector('.toc details');
  if (toc) {
    const links = [...toc.querySelectorAll('a')];
    function highlightTarget() {
      for (const link of links) {
        if (link.hash === location.hash) {
          link.setAttribute('aria-current', 'location');
          toc.open = true;
        }
        else link.removeAttribute('aria-current');
      }
    }
    window.addEventListener('hashchange', highlightTarget);
    highlightTarget();
  }
})();
