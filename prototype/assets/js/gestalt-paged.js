(() => {
  const story = document.querySelector('.gestalt-story');
  const header = document.querySelector('.site-header');
  const pages = [...story.querySelectorAll('.gs-page')];
  const segments = [...story.querySelectorAll('.gs-seg')];
  const progress = story.querySelector('#prog');
  const label = story.querySelector('#progLabel');
  const previous = story.querySelector('#progPrev');
  const next = story.querySelector('#progNext');
  const map = story.querySelector('#mapov');
  const mapButton = story.querySelector('#mapBtn');
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  let current = -1;
  let frame = 0;

  function updateProgress() {
    frame = 0;
    const page = pages[current];
    const remaining = page.offsetHeight - innerHeight + header.offsetHeight + progress.offsetHeight;
    const fraction = remaining > 0
      ? Math.max(0, Math.min(1, -page.getBoundingClientRect().top / remaining))
      : 1;

    segments.forEach((segment, index) => {
      segment.style.setProperty('--f', index < current ? 1 : index === current ? fraction : 0);
    });

    if (motion.matches) return;
    page.querySelectorAll('[data-swap]').forEach((figure) => {
      const section = figure.closest('.gs-split');
      const bounds = section.getBoundingClientRect();
      const position = (innerHeight * .55 - bounds.top) / Math.max(bounds.height, 1);
      figure.style.setProperty('--swap', Math.max(0, Math.min(1, (position - .3) / .3)));
    });
  }

  function scheduleProgress() {
    if (!frame) frame = requestAnimationFrame(updateProgress);
  }

  const reveal = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      entry.target.classList.add('is-in');
      reveal.unobserve(entry.target);
    }
  }, { threshold: .1 });
  story.querySelectorAll('.gs-wc-breathe, .gs-fan__item, .gs-replicas li, .gs-ways').forEach((element) => {
    reveal.observe(element);
  });

  function showPage(index, target, moveFocus = false) {
    const page = pages[index];
    if (current !== index) {
      pages.forEach((item, position) => { item.hidden = position !== index; });
      current = index;
      label.textContent = page.dataset.label;
      progress.hidden = index === 0;
      for (const [link, adjacent] of [[previous, pages[index - 1]], [next, pages[index + 1]]]) {
        link.hidden = !adjacent;
        if (adjacent) link.href = '#' + adjacent.id;
      }
      document.title = (index === 0 ? '' : page.dataset.label + ' – ') + 'Гештальт простыми словами – Маргарита Терво';
    }

    if (moveFocus) {
      const heading = target?.querySelector('h1, h2, h3') || page.querySelector('h1, h2, h3');
      heading.tabIndex = -1;
      heading.focus({ preventScroll: true });
    }

    if (target && target !== page) target.scrollIntoView({ block: 'start', behavior: 'instant' });
    else window.scrollTo({ top: 0, behavior: 'instant' });
    scheduleProgress();
  }

  function readHash() {
    const id = location.hash.slice(1);
    const target = document.getElementById(id);
    const index = pages.indexOf(target?.closest('.gs-page'));
    if (index >= 0) showPage(index, target);
    else if (!id || current < 0) showPage(0);
  }

  function followPage(index, target) {
    const hash = '#' + target.id;
    if (location.hash !== hash) history.pushState(null, '', hash);
    showPage(index, target, true);
  }

  story.addEventListener('click', (event) => {
    const link = event.target.closest('a[href^="#"]');
    if (!link || event.defaultPrevented || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const target = document.getElementById(link.hash.slice(1));
    const index = pages.indexOf(target?.closest('.gs-page'));
    if (index < 0) return;

    event.preventDefault();
    if (map.open) map.close();
    followPage(index, target);
  });

  mapButton.addEventListener('click', () => {
    map.showModal();
    mapButton.setAttribute('aria-expanded', 'true');
  });
  story.querySelector('#mapClose').addEventListener('click', () => map.close());
  map.addEventListener('close', () => mapButton.setAttribute('aria-expanded', 'false'));

  window.addEventListener('keydown', (event) => {
    if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey || map.open) return;
    if (event.target.closest?.('input, textarea, select, [contenteditable], .site-header')) return;
    const direction = event.key === 'ArrowLeft' ? -1 : event.key === 'ArrowRight' ? 1 : 0;
    const adjacent = pages[current + direction];
    if (!direction || !adjacent) return;
    event.preventDefault();
    followPage(current + direction, adjacent);
  });

  new ResizeObserver(() => {
    document.documentElement.style.setProperty('--gestalt-header-height', header.offsetHeight + 'px');
    scheduleProgress();
  }).observe(header);
  window.addEventListener('scroll', scheduleProgress, { passive: true });
  window.addEventListener('resize', scheduleProgress);
  window.addEventListener('hashchange', readHash);
  readHash();
})();
