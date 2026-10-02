// Portable story locale selection. The English source remains visible and labeled
// until an authored zh-CN companion exists for that group.
(() => {
  const key = 'tb3-presentation-language';
  const choice = document.querySelector('#story-language');
  const english = document.querySelector('[data-story-locale="en"]');
  const chinese = document.querySelector('[data-story-locale="zh-CN"]');
  const fallback = document.querySelector('#story-translation-notice');
  const valid = (value) => value === 'en' || value === 'zh-CN';
  let saved;
  try {
    saved = localStorage.getItem(key);
  } catch {
    /* file storage may be unavailable */
  }
  const query = new URLSearchParams(location.search).get('lang');
  const initial = valid(query)
    ? query
    : valid(saved)
      ? saved
      : navigator.language.toLowerCase().startsWith('zh')
        ? 'zh-CN'
        : 'en';
  function show(locale, updateUrl = false) {
    const translated = locale === 'zh-CN' && !!chinese;
    english.hidden = translated;
    if (chinese) chinese.hidden = !translated;
    fallback.hidden = locale !== 'zh-CN' || translated;
    document.documentElement.lang = translated ? 'zh-CN' : 'en';
    choice.value = locale;
    document.querySelectorAll('[data-en][data-zh]').forEach((node) => {
      node.textContent = node.dataset[translated ? 'zh' : 'en'];
    });
    try {
      localStorage.setItem(key, locale);
    } catch {
      /* URL still carries choice */
    }
    if (updateUrl) {
      const url = new URL(location.href);
      url.searchParams.set('lang', locale);
      history.replaceState(history.state, '', url.href);
    }
    document.querySelectorAll('a[href^="../"], a[data-story-link]').forEach((link) => {
      link.dataset.storyLink ||= link.getAttribute('href');
      const target = new URL(link.dataset.storyLink, location.href);
      target.searchParams.set('lang', locale);
      link.href = target.href;
    });
  }
  choice.addEventListener('change', () => show(choice.value, true));
  show(initial);
})();
